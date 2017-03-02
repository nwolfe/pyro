import json
import libtcodpy as libtcod
from pyro.ai import Aggressive, AggressiveSpellcaster, PassiveAggressive, Confused
from pyro.components import AI, Experience, Fighter, Item, Equipment, SpellItemUse, Spellcaster
from pyro.spells import Confuse, Fireball, Heal, LightningBolt
from pyro.gameobject import GameObject
from pyro.events import EventListener
from pyro.settings import RENDER_ORDER_CORPSE, RENDER_ORDER_ITEM


MONSTER_AI_CLASSES = dict(
    aggressive=Aggressive,
    aggressive_spellcaster=AggressiveSpellcaster,
    passive_aggressive=PassiveAggressive,
    confused=Confused
)

MONSTER_SPELLS = dict(
    lightning_bolt=LightningBolt,
    fireball=Fireball
)

ITEM_USES = dict(
    cast_heal=Heal,
    cast_lightning_bolt=LightningBolt,
    cast_confuse=Confuse,
    cast_fireball=Fireball
)


def monster_death(monster, attacker, game):
    # Transform it into a nasty corpse!
    # It doesn't block, can't be attacked, and doesn't move
    exp = monster.component(Experience)
    if attacker == game.player:
        game.message('The {0} is dead! You gain {1} experience points.'.
                     format(monster.name, exp.xp), libtcod.orange)
    else:
        game.message('The {0} is dead!'.format(monster.name), libtcod.orange)
    attacker.component(Experience).xp += exp.xp
    monster.glyph = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.render_order = RENDER_ORDER_CORPSE
    monster.name = 'Remains of {0}'.format(monster.name)
    monster.remove_component(Fighter)
    monster.remove_component(AI)


class MonsterDeath(EventListener):
    def handle_event(self, source, event, context):
        if event == 'death':
            monster_death(source, context['attacker'], source.game)


def instantiate_spell(spell_template):
    if type(spell_template) is dict:
        spell = MONSTER_SPELLS[spell_template['name']]()
        spell.configure(spell_template)
    else:
        spell = MONSTER_SPELLS[spell_template]()
        spell.configure_monster_defaults()
    return spell


def instantiate_monster(template):
    name = template['name']
    glyph = template['glyph']
    color = getattr(libtcod, template['color'])
    ai_comp = MONSTER_AI_CLASSES[template['ai']]()
    exp_comp = Experience(template['experience'])
    fighter_comp = Fighter(template['hp'], template['defense'], template['power'])
    components = [fighter_comp, ai_comp, exp_comp]
    if 'spell' in template:
        spell = instantiate_spell(template['spell'])
        components.append(Spellcaster(spell))
    return GameObject(glyph=glyph, name=name, color=color, blocks=True,
                      components=components, listeners=[MonsterDeath()])


def make_monster(name, monster_templates):
    for template in monster_templates:
        if template['name'] == name:
            return instantiate_monster(template)


def load_templates(json_file):
    with open(json_file) as f:
        templates = json.load(f)

        # For some reason the UI renderer can't handle Unicode strings so we
        # need to convert the character glyph to UTF-8 for it to be rendered
        for t in templates:
            t['glyph'] = str(t['glyph'])

        return templates


def instantiate_item(template):
    name = template['name']
    glyph = template['glyph']
    color = getattr(libtcod, template['color'])
    if 'slot' in template:
        equipment = Equipment(slot=template['slot'])
        if 'power' in template:
            equipment.power_bonus = template['power']
        if 'defense' in template:
            equipment.defense_bonus = template['defense']
        if 'hp' in template:
            equipment.max_hp_bonus = template['hp']
        return GameObject(glyph=glyph, name=name, color=color,
                          render_order=RENDER_ORDER_ITEM,
                          components=[equipment])
    elif 'on_use' in template:
        spell = ITEM_USES[template['on_use']]()
        item = Item(on_use=SpellItemUse(spell))
        return GameObject(glyph=glyph, name=name, color=color,
                          render_order=RENDER_ORDER_ITEM,
                          components=[item])


def make_item(name, item_templates):
    for template in item_templates:
        if template['name'] == name:
            return instantiate_item(template)


class GameObjectFactory:
    def __init__(self):
        self.monster_templates = None
        self.item_templates = None

    def load_templates(self, monster_file, item_file):
        self.monster_templates = load_templates(monster_file)
        self.item_templates = load_templates(item_file)

    def new_monster(self, monster_name):
        return make_monster(monster_name, self.monster_templates)

    def new_item(self, item_name):
        return make_item(item_name, self.item_templates)
