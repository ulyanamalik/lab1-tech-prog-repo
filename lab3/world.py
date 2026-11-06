from dataclasses import dataclass
from abc import ABC, abstractmethod
from .core import Dice, Outcome
from .items import Item, ItemCatalog
from .characters import Enemy, Goblin, Skeleton, Dragon, HauntedWeapon, LegendaryEnemy, WindfuryEnemy, ArmoredEnemy
from .combat import Battle, BalancedTactic, BattleReport

@dataclass(frozen=True)
class Rewards:
    experience: int; gold: int; loot: Item | None; levels_gained: int

@dataclass(frozen=True)
class ExpeditionReport:
    seed: int; location_code: str; tactic_code: str; battle: BattleReport; rewards: Rewards

class Location(ABC):
    def __init__(self, code, display_name, rec_level, catalog):
        self._code=code; self._display_name=display_name; self._rec_level=rec_level; self._catalog=catalog
    @abstractmethod
    def _create_enemy(self) -> Enemy: ...
    @property
    @abstractmethod
    def _loot_table(self) -> tuple[str, ...]: ...
    def explore(self, hero, seed=None, tactic=None):
        d = Dice()
        if seed is None: seed = d.next_seed()
        d.reseed(seed); t = tactic or BalancedTactic(); hero.rest(); e = self._create_enemy()
        if d.chance(0.2):
            both = d.chance(0.25)
            if d.chance(0.5): e = LegendaryEnemy(e); e = WindfuryEnemy(e) if both else e
            else: e = WindfuryEnemy(e); e = LegendaryEnemy(e) if both else e
            if d.chance(0.3): e = ArmoredEnemy(e)
        b = Battle(hero, e, t).run()
        if b.outcome == Outcome.VICTORY:
            loot = self._catalog.create(d.pick(self._loot_table)) if d.chance(0.6) else None
            if loot and d.chance(0.3): loot.enchant(d.pick(loot.possible_enchantments))
            r = Rewards(e.experience_reward, e.roll_gold_reward(), loot, hero.gain_experience(e.experience_reward))
            hero.add_gold(r.gold)
            if loot: hero.add_item(loot)
        else:
            lost = hero.gold // 2; hero.spend_gold(lost); r = Rewards(0, -lost, None, 0)
        return ExpeditionReport(seed, self._code, t.code, b, r)
    @property
    def code(self): return self._code
    @property
    def display_name(self): return self._display_name
    @property
    def recommended_level(self): return self._rec_level

class Forest(Location):
    def __init__(self, c): super().__init__("forest", "Мистический лес", 1, c)
    def _create_enemy(self): return Goblin()
    @property
    def _loot_table(self): return ("goblin-cleaver", "hunting-bow", "leather-armor")

class Crypt(Location):
    def __init__(self, c): super().__init__("crypt", "Заброшенный склеп", 3, c)
    def _create_enemy(self): return Skeleton()
    @property
    def _loot_table(self): return ("knight-blade", "bone-bow", "necromancer-staff", "crypt-mail")

class DragonLair(Location):
    def __init__(self, c): super().__init__("dragon-lair", "Логово дракона", 5, c)
    def _create_enemy(self): return Dragon()
    @property
    def _loot_table(self): return ("dawn-blade", "dragonscale-armor")

class HauntedManor(Location):
    def __init__(self, c): super().__init__("haunted-manor", "Проклятый особняк", 2, c)
    def _create_enemy(self): return HauntedWeapon(self._catalog.create_weapon(Dice().pick(("iron-sword", "elven-bow", "ember-staff"))))
    @property
    def _loot_table(self): return ("iron-sword", "elven-bow", "ember-staff")