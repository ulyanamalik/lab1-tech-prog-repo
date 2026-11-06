import json
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from .core import UnknownCodeError, Outcome
from .items import ItemCatalog, create_default_catalog, get_enchantment_by_code
from .characters import Hero, HeroClass, Achievement
from .world import Forest, Crypt, DragonLair, HauntedManor, ExpeditionReport
from .combat import Tactic, BalancedTactic, AggressiveTactic, CautiousTactic

class GameEventType(Enum): VICTORY="victory"; DEFEAT="defeat"; LEVEL_UP="level-up"

@dataclass(frozen=True)
class GameEvent:
    type: GameEventType; hero: Hero; expedition: ExpeditionReport

class GameEventPublisher:
    def __init__(self): self._listeners = {}
    def subscribe(self, t, l): self._listeners.setdefault(t, []).append(l)
    def publish(self, e):
        for l in self._listeners.get(e.type, []): l.on_event(e)

class AchievementTracker:
    def on_event(self, e):
        h = e.hero
        if e.type == GameEventType.VICTORY:
            h.unlock(Achievement.FIRST_BLOOD)
            if e.expedition.battle.enemy.code == "dragon": h.unlock(Achievement.DRAGON_SLAYER)
            if e.expedition.rewards.loot and e.expedition.rewards.loot.enchantments: h.unlock(Achievement.LUCKY)
        elif e.type == GameEventType.LEVEL_UP and h.level >= 5: h.unlock(Achievement.VETERAN)

class ExpeditionJournal:
    def __init__(self): self._entries = {}
    def on_event(self, e): self._entries.setdefault(e.hero.name, []).append(e.expedition)
    def get_entries(self, name): return tuple(self._entries.get(name, []))

class FileHeroRepository:
    def __init__(self, file: Path, catalog: ItemCatalog): self._file = file; self._catalog = catalog
    def find_by_name(self, name): return next((h for h in self.find_all() if h.name == name), None)
    def find_all(self):
        if not self._file.exists(): return []
        text = self._file.read_text(encoding="utf-8")
        if not text.strip(): return []
        return [self._restore(s) for s in json.loads(text)]
    def save(self, hero):
        saves = [self._snapshot(h) for h in self.find_all() if h.name != hero.name]
        saves.append(self._snapshot(hero)); self._file.parent.mkdir(parents=True, exist_ok=True)
        self._file.write_text(json.dumps(saves, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    def _snap_item(self, item): return {"code": item.code, "enchantments": [e.code for e in item.enchantments]}
    def _snapshot(self, hero):
        return {"name": hero.name, "heroClass": hero.hero_class.code, "level": hero.level,
                "experience": hero.experience, "gold": hero.gold, "weapon": self._snap_item(hero.weapon),
                "armor": self._snap_item(hero.armor), "inventory": [self._snap_item(i) for i in hero.inventory],
                "achievements": [a.code for a in hero.achievements]}
    def _restore_item(self, save):
        item = self._catalog.create(save["code"])
        for c in save["enchantments"]: item.enchant(get_enchantment_by_code(c))
        return item
    def _restore(self, save):
        return (Hero.Builder().set_name(save["name"]).set_hero_class(HeroClass.by_code(save["heroClass"]))
                .set_level(save["level"]).set_experience(save["experience"]).set_gold(save["gold"])
                .set_weapon(self._restore_item(save["weapon"])).set_armor(self._restore_item(save["armor"]))
                .set_inventory([self._restore_item(i) for i in save["inventory"]])
                .set_achievements([Achievement.by_code(c) for c in save["achievements"]]).build())

class CachingHeroRepository:
    def __init__(self, target): self._target = target; self._cache = None
    def _cached(self):
        if self._cache is None: self._cache = {h.name: h for h in self._target.find_all()}
        return self._cache
    def find_by_name(self, name): return self._cached().get(name)
    def find_all(self): return list(self._cached().values())
    def save(self, hero): self._target.save(hero); self._cached()[hero.name] = hero

class Merchant:
    def __init__(self, catalog, assortment): self._catalog = catalog; self._assortment = assortment
    @property
    def showcase(self): return [self._catalog.create(c) for c in self._assortment]
    def buy(self, hero, code):
        if code not in self._assortment: raise UnknownCodeError("Товар", code)
        i = self._catalog.create(code); hero.spend_gold(i.price); hero.add_item(i); return i
    def sell(self, hero, item):
        p = item.price * 50 // 100; hero.remove_item(item); hero.add_gold(p); return p

class GameFacade:
    def __init__(self, save_file):
        self._cat = create_default_catalog()
        self._locs = [Forest(self._cat), HauntedManor(self._cat), Crypt(self._cat), DragonLair(self._cat)]
        self.tactics = (BalancedTactic(), AggressiveTactic(), CautiousTactic())
        self._merchant = Merchant(self._cat, ["iron-sword", "elven-bow", "ember-staff", "chainmail", "plate-armor"])
        self._heroes = CachingHeroRepository(FileHeroRepository(save_file, self._cat))
        self._events = GameEventPublisher(); self._journal = ExpeditionJournal(); ach = AchievementTracker()
        self._events.subscribe(GameEventType.VICTORY, ach); self._events.subscribe(GameEventType.LEVEL_UP, ach)
        self._events.subscribe(GameEventType.VICTORY, self._journal); self._events.subscribe(GameEventType.DEFEAT, self._journal)
    @property
    def locations(self): return self._locs
    def get_starter_kit(self, code):
        kit = HeroClass.by_code(code).starter_kit(self._cat); return kit.create_weapon(), kit.create_armor()
    @property
    def showcase(self): return self._merchant.showcase
    def sell_price(self, item): return item.price * 50 // 100
    @property
    def heroes(self): return self._heroes.find_all()
    def get_hero(self, name):
        h = self._heroes.find_by_name(name)
        if not h: raise ValueError("Нет героя")
        return h
    def create_hero(self, name, code):
        if self._heroes.find_by_name(name): raise ValueError("Герой уже есть")
        hc = HeroClass.by_code(code)
        h = Hero.Builder().set_name(name).set_hero_class(hc).set_starter_kit(hc.starter_kit(self._cat)).build()
        self._heroes.save(h); return h
    def explore(self, hero_name, loc_code, tactic_code):
        h = self.get_hero(hero_name); l = next(x for x in self._locs if x.code == loc_code)
        t = next(x for x in self.tactics if x.code == tactic_code)
        r = l.explore(h, tactic=t)
        res = GameEventType.VICTORY if r.battle.outcome == Outcome.VICTORY else GameEventType.DEFEAT
        self._events.publish(GameEvent(res, h, r))
        if r.rewards.levels_gained > 0: self._events.publish(GameEvent(GameEventType.LEVEL_UP, h, r))
        self._heroes.save(h); return r
    def equip(self, hero_name, idx):
        h = self.get_hero(hero_name); i = h.inventory[idx]; h.equip(i); self._heroes.save(h); return i
    def buy(self, hero_name, code):
        h = self.get_hero(hero_name); i = self._merchant.buy(h, code); self._heroes.save(h); return i
    def sell(self, hero_name, idx):
        h = self.get_hero(hero_name); p = self._merchant.sell(h, h.inventory[idx]); self._heroes.save(h); return p
    def get_journal(self, name): return self._journal.get_entries(name)