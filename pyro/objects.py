import json
import tcod as libtcod
from pyro.engine.item import Item, Equipment, SpellItemUse
from pyro.engine.glyph import Glyph
from pyro.spells import Confuse, Fireball, Heal, LightningBolt
from pyro.engine import ai, Hero, Monster

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


def load_templates(json_file):
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


class _GameObjectFactory:
    def __init__(self, monster_file, item_file, player_file):
        self.monster_templates = load_templates(monster_file)
        self.item_templates = load_templates(item_file)
        self._player_template = load_templates(player_file)
        self.game = None

    def new_monster(self, monster_name, position=None):
        for template in self.monster_templates:
            if template['name'] == monster_name:
                monster = self._instantiate_monster(template)
                if position:
                    monster.pos.copy(position)
                return monster
        return None

    def new_item(self, item_name, position=None):
        for template in self.item_templates:
            if template['name'] == item_name:
                item = self._instantiate_item(template)
                if position:
                    item.pos.copy(position)
                return item
        return None

    def new_player(self):
        hero = Hero(self.game)
        hero.name = self._player_template['name']
        hero.inventory = []
        hero.glyph = Glyph(self._player_template['glyph'],
                           getattr(libtcod, self._player_template['color']))
        hero.hp = self._player_template['hp']
        hero.base_max_hp = hero.hp
        hero.base_defense = self._player_template['defense']
        hero.base_power = self._player_template['power']
        self.game.player = hero
        for item in self._player_template['starting_items']:
            self.new_item(item).pick_up(hero)
        return hero

    def _instantiate_monster(self, template):
        name = template['name']
        spells = None
        if 'spell' in template:
            spells = [self._instantiate_spell(template['spell'])]
        elif 'spells' in template:
            spells = [self._instantiate_spell(spell) for spell in template['spells']]
        monster = Monster(self.game)
        monster.name = name
        monster.ai = ai.new(template['ai'], spells)
        monster.ai.monster = monster
        monster.glyph = Glyph(template['glyph'], getattr(libtcod, template['color']))
        monster.xp = template['experience']
        monster.hp = template['hp']
        monster.base_max_hp = monster.hp
        monster.base_defense = template['defense']
        monster.base_power = template['power']
        return monster

    def _instantiate_item(self, template):
        name = template['name']
        glyph = Glyph(template['glyph'], getattr(libtcod, template['color']))
        if 'slot' in template:
            equipment = Equipment(name, glyph, slot=template['slot'])
            if 'power' in template:
                equipment.power_bonus = template['power']
            if 'defense' in template:
                equipment.defense_bonus = template['defense']
            if 'hp' in template:
                equipment.max_hp_bonus = template['hp']
            return equipment
        elif 'on_use' in template:
            spell = self._instantiate_spell(ITEM_USES[template['on_use']])
            return Item(name, glyph, on_use=SpellItemUse(spell))

    def _instantiate_spell(self, template):
        if type(template) is dict:
            spell = SPELLS[template['name']]()
            spell.configure(template)
        else:
            spell = SPELLS[template]()
        return spell


FACTORY = _GameObjectFactory(monster_file='resources/monsters.json',
                             item_file='resources/items.json',
                             player_file='resources/player.json')
