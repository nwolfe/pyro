import libtcodpy as libtcod
import json
from pyro.gameobject import GameObject
import pyro.abilities
import pyro.ai.confused
import pyro.ai.aggressive
import pyro.ai.aggressive_spellcaster
import pyro.ai.passive_aggressive
import pyro.components.ai as libai
import pyro.components.experience as libxp
import pyro.components.fighter as libfighter
import pyro.components.item as libitem
import pyro.components.spellcaster as libcast
import pyro.spells
from pyro.settings import *


def monster_death(monster, game):
    # Transform it into a nasty corpse!
    # It doesn't block, can't be attacked, and doesn't move
    exp = monster.component(libxp.Experience)
    game.message('The {0} is dead! You gain {1} experience points.'.
                 format(monster.name.capitalize(), exp.xp),
                 libtcod.orange)
    game.player.component(libxp.Experience).xp += exp.xp
    monster.glyph = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.render_order = 0
    monster.name = 'remains of {0}'.format(monster.name)
    monster.components.pop(libfighter.Fighter)
    monster.components.pop(libai.AI)


MONSTER_AI_CLASSES = dict(
    aggressive=pyro.ai.aggressive.Aggressive,
    aggressive_spellcaster=pyro.ai.aggressive_spellcaster.AggressiveSpellcaster,
    passive_aggressive=pyro.ai.passive_aggressive.PassiveAggressive,
    confused=pyro.ai.confused.Confused
)


def instantiate_monster(template):
    name = template['name']
    glyph = template['glyph']
    color = getattr(libtcod, template['color'])
    ai_comp = MONSTER_AI_CLASSES[template['ai']]()
    exp_comp = libxp.Experience(template['experience'])
    fighter_comp = libfighter.Fighter(template['hp'], template['defense'],
                                      template['power'], death_fn=monster_death)
    components = {libfighter.Fighter: fighter_comp,
                  libai.AI: ai_comp,
                  libxp.Experience: exp_comp}
    if 'spell' in template:
        spell_fn = getattr(pyro.spells, template['spell'])
        spell = spell_fn()
        components[libcast.Spellcaster] = libcast.Spellcaster(spell)
    return GameObject(glyph=glyph, name=name, color=color, blocks=True,
                      components=components)


def make_monster(name, monster_templates):
    for template in monster_templates:
        if template['name'] == name:
            return instantiate_monster(template)


def load_templates(file):
    with open(file) as f:
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
        equipment = libitem.Equipment(slot=template['slot'])
        if 'power' in template:
            equipment.power_bonus = template['power']
        if 'defense' in template:
            equipment.defense_bonus = template['defense']
        if 'hp' in template:
            equipment.max_hp_bonus = template['hp']
        return GameObject(glyph=glyph, name=name, color=color, render_order=0,
                          components={libitem.Equipment: equipment})
    elif 'on_use' in template:
        use_fn = getattr(pyro.abilities, template['on_use'])
        return GameObject(glyph=glyph, name=name, color=color, render_order=0,
                          components={libitem.Item: libitem.Item(use_fn=use_fn)})


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
