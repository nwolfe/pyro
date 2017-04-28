import json
import tcod as libtcod
import pyro.components.ai
from pyro.components import Experience, Item, Equipment, Inventory
from pyro.components import SpellItemUse, Physics
from pyro.engine.glyph import Glyph
from pyro.spells import Confuse, Fireball, Heal, LightningBolt
from pyro.gameobject import GameObject
from pyro.settings import PLAYER_DEFAULT_HP, PLAYER_DEFAULT_DEFENSE, PLAYER_DEFAULT_POWER
from pyro.engine import Hero, Monster

SPELLS = dict(
    confuse=Confuse,
    fireball=Fireball,
    heal=Heal,
    lightning_bolt=LightningBolt
)

ITEM_USES = dict(
    cast_heal='heal',
    cast_lightning_bolt='lightning_bolt',
    cast_confuse='confuse',
    cast_fireball='fireball'
)


def instantiate_spell(template):
    if type(template) is dict:
        spell = SPELLS[template['name']]()
        spell.configure(template)
    else:
        spell = SPELLS[template]()
    return spell


def instantiate_monster(template, game):
    name = template['name']
    exp_comp = Experience(template['experience'])
    spells = None
    if 'spell' in template:
        spells = [instantiate_spell(template['spell'])]
    elif 'spells' in template:
        spells = [instantiate_spell(spell) for spell in template['spells']]
    ai_comp = pyro.components.ai.new(template['ai'], spells)
    components = [ai_comp, exp_comp, Physics(blocks=True)]
    game_object = GameObject(name=name, components=components, game=game)
    monster = Monster(game, game_object)
    monster.glyph = Glyph(template['glyph'], getattr(libtcod, template['color']))
    monster.hp = template['hp']
    monster.base_max_hp = monster.hp
    monster.base_defense = template['defense']
    monster.base_power = template['power']
    game_object.actor = monster
    return monster


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
    components = [Physics()]
    if 'slot' in template:
        equipment = Equipment(slot=template['slot'])
        if 'power' in template:
            equipment.power_bonus = template['power']
        if 'defense' in template:
            equipment.defense_bonus = template['defense']
        if 'hp' in template:
            equipment.max_hp_bonus = template['hp']
        components.append(equipment)
    elif 'on_use' in template:
        spell = instantiate_spell(ITEM_USES[template['on_use']])
        item = Item(on_use=SpellItemUse(spell))
        components.append(item)
    item = GameObject(name=name, components=components)
    item.glyph = Glyph(template['glyph'], getattr(libtcod, template['color']))
    return item


def make_player(game):
    components = [
        Experience(xp=0, level=1),
        Inventory(items=[]),
        Physics(blocks=True)
    ]
    player = GameObject('Player', components, game=game)
    hero = Hero(game, player)
    hero.glyph = Glyph('@', libtcod.white)
    hero.hp = PLAYER_DEFAULT_HP
    hero.base_max_hp = hero.hp
    hero.base_defense = PLAYER_DEFAULT_DEFENSE
    hero.base_power = PLAYER_DEFAULT_POWER
    player.actor = hero
    game.player = hero
    return hero


class GameObjectFactory:
    def __init__(self, game=None):
        self.monster_templates = None
        self.item_templates = None
        self.game = game

    def load_templates(self, monster_file, item_file):
        self.monster_templates = load_templates(monster_file)
        self.item_templates = load_templates(item_file)

    def new_monster(self, monster_name):
        for template in self.monster_templates:
            if template['name'] == monster_name:
                return instantiate_monster(template, self.game)
        return None

    def new_item(self, item_name):
        for template in self.item_templates:
            if template['name'] == item_name:
                item = instantiate_item(template)
                item.game = self.game
                return item
        return None
