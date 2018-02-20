import os
import json
import tcod as libtcod
from pyro.engine.item import Item, SpellItemUse
from pyro.engine.glyph import glyph
from pyro.spells import Confuse, Fireball, Heal, LightningBolt
from pyro.engine import ai, Hero, Monster


def new_player(game):
    hero = Hero(game)
    hero.name = PLAYER_TEMPLATE['name']
    hero.inventory = []
    hero.glyph = glyph(PLAYER_TEMPLATE['glyph'],
                       getattr(libtcod, PLAYER_TEMPLATE['color']))
    hero.hp = PLAYER_TEMPLATE['hp']
    hero.base_max_hp = hero.hp
    hero.base_defense = PLAYER_TEMPLATE['defense']
    hero.base_power = PLAYER_TEMPLATE['power']
    game.player = hero
    for i in PLAYER_TEMPLATE['starting_items']:
        # TODO Don't reimplement this here
        item = new_item(i)
        item.owner = hero
        hero.inventory.append(item)
        if item.can_equip():
            item.is_equipped = True
    return hero


def new_monster(game, monster_id, position=None):
    for template in MONSTER_TEMPLATES:
        if template['id'] == monster_id:
            monster = _instantiate_monster(game, template)
            if position:
                monster.pos.copy(position)
            return monster
    return None


def new_item(item_id, position=None):
    for template in ITEM_TEMPLATES:
        if template['id'] == item_id:
            item = _instantiate_item(template)
            if position:
                item.pos.copy(position)
            return item
    return None


def _load_templates(json_file):
    with open(json_file) as f:
        templates = json.load(f)

        # For some reason the UI renderer can't handle Unicode strings so we
        # need to convert the character glyph to UTF-8 for it to be rendered
        if type(templates) is list:
            for t in templates:
                t['glyph'] = str(t['glyph'])
        elif type(templates) is dict:
            templates['glyph'] = str(templates['glyph'])

        return templates


if 'MONSTER_TEMPLATES' in os.environ:
    MONSTER_TEMPLATES = _load_templates(os.environ['MONSTER_TEMPLATES'])
else:
    MONSTER_TEMPLATES = _load_templates('resources/monsters.json')

if 'ITEM_TEMPLATES' in os.environ:
    ITEM_TEMPLATES = _load_templates(os.environ['ITEM_TEMPLATES'])
else:
    ITEM_TEMPLATES = _load_templates('resources/items.json')

if 'PLAYER_TEMPLATE' in os.environ:
    PLAYER_TEMPLATE = _load_templates(os.environ['PLAYER_TEMPLATE'])
else:
    PLAYER_TEMPLATE = _load_templates('resources/player.json')


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


def _instantiate_monster(game, template):
    name = template['name']
    spells = None
    if 'spell' in template:
        spells = [_instantiate_spell(template['spell'])]
    elif 'spells' in template:
        spells = [_instantiate_spell(spell) for spell in template['spells']]
    monster = Monster(game)
    monster.name = name
    monster.ai = ai.new(template['ai'], spells)
    monster.ai.monster = monster
    monster.glyph = glyph(template['glyph'], getattr(libtcod, template['color']))
    monster.xp = template['experience']
    monster.hp = template['hp']
    monster.base_max_hp = monster.hp
    monster.base_defense = template['defense']
    monster.base_power = template['power']
    return monster


def _instantiate_item(template):
    name = template['name']
    glyph_ = glyph(template['glyph'], getattr(libtcod, template['color']))
    item = Item(name, glyph_)
    if 'slot' in template:
        item.equip_slot = template['slot']
        if 'power' in template:
            item.power_bonus = template['power']
        if 'defense' in template:
            item.defense_bonus = template['defense']
        if 'hp' in template:
            item.max_hp_bonus = template['hp']
    elif 'on_use' in template:
        spell = _instantiate_spell(ITEM_USES[template['on_use']])
        item.on_use = SpellItemUse(spell)
    return item


def _instantiate_spell(template):
    if type(template) is dict:
        spell = SPELLS[template['name']]()
        spell.configure(template)
    else:
        spell = SPELLS[template]()
    return spell
