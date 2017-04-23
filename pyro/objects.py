import json
import tcod as libtcod
import pyro.components.ai
from pyro.components import Experience, Item, Equipment, Inventory
from pyro.components import SpellItemUse, Graphics, Physics
from pyro.spells import Confuse, Fireball, Heal, LightningBolt
from pyro.gameobject import GameObject
from pyro.settings import RENDER_ORDER_ITEM
from pyro.settings import PLAYER_DEFAULT_HP, PLAYER_DEFAULT_DEFENSE, PLAYER_DEFAULT_POWER
from pyro.engine import Hero

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


def instantiate_monster(template):
    name = template['name']
    exp_comp = Experience(template['experience'])
    graphics_comp = Graphics(template['glyph'], getattr(libtcod, template['color']))
    spells = None
    if 'spell' in template:
        spells = [instantiate_spell(template['spell'])]
    elif 'spells' in template:
        spells = [instantiate_spell(spell) for spell in template['spells']]
    ai_comp = pyro.components.ai.new(template['ai'], spells)
    components = [ai_comp, exp_comp, graphics_comp, Physics(blocks=True)]
    return GameObject(name=name, components=components, hp=template['hp'],
                      defense=template['defense'], power=template['power'])


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
    graphics = Graphics(glyph, color, RENDER_ORDER_ITEM)
    components = [Physics(), graphics]
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
    return GameObject(name=name, components=components)


def make_item(name, item_templates):
    for template in item_templates:
        if template['name'] == name:
            return instantiate_item(template)


def make_player(game):
    components = [
        Experience(xp=0, level=1),
        Graphics(glyph='@', color=libtcod.white),
        Inventory(items=[]),
        Physics(blocks=True)
    ]
    player = GameObject('Player', components, hp=PLAYER_DEFAULT_HP,
                        defense=PLAYER_DEFAULT_DEFENSE, power=PLAYER_DEFAULT_POWER,
                        game=game)
    hero = Hero(game, player)
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
        monster = make_monster(monster_name, self.monster_templates)
        monster.game = self.game
        return monster

    def new_item(self, item_name):
        item = make_item(item_name, self.item_templates)
        item.game = self.game
        return item
