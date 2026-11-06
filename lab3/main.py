from pathlib import Path
from .core import EventType, Outcome
from .characters import HeroClass
from .game_systems import GameFacade

class ConsoleView:
    def describe(self, item):
        d = item.name
        if item.enchantments: d += " [" + ", ".join(e.name for e in item.enchantments) + "]"
        return d + " (" + item.description + ")"
    def print_hero(self, hero):
        print(f"{hero.name}, {hero.hero_class.display_name} {hero.level} ур. | здоровье {hero.max_health} | опыт {hero.experience}/{hero.experience_to_next_level} | золото {hero.gold}")
        print("  Оружие: " + self.describe(hero.weapon)); print("  Броня:  " + self.describe(hero.armor))
        if hero.achievements: print("  Достижения: " + ", ".join(a.display_name for a in hero.achievements))
    def print_report(self, r, loc_name):
        b = r.battle
        print(f"=== {loc_name} (сид {r.seed}) ===")
        print(f"{b.hero.name} встречает врага: {b.enemy.name} ({b.enemy.max_health} здоровья)")
        for e in b.events:
            s = b.hero.name if e.source.name == 'HERO' else b.enemy.name
            t = b.hero.name if e.target.name == 'HERO' else b.enemy.name
            if e.type == EventType.HIT: print(f"[раунд {e.round}] {s} -> {t}: {e.amount} урона, осталось {e.target_health_after}")
            elif e.type == EventType.CRITICAL_HIT: print(f"[раунд {e.round}] {s} -> {t}: КРИТ! {e.amount} урона, осталось {e.target_health_after}")
            elif e.type == EventType.EVADE: print(f"[раунд {e.round}] {s} -> {t}: промах")
            elif e.type == EventType.ABSORB: print(f"[раунд {e.round}] {s} -> {t}: барьер поглотил {e.amount} урона")
            elif e.type == EventType.POWER_STRIKE: print(f"[раунд {e.round}] {s} бьет в полную силу!")
            elif e.type == EventType.DEFEND: print(f"[раунд {e.round}] {s} уходит в оборону")
            elif e.type == EventType.DEATH: print(f"{t} повержен!")
        if b.outcome == Outcome.DEFEAT: print(f"Поражение... {b.hero.name} теряет {-r.rewards.gold} золота")
        else:
            print(f"Победа! +{r.rewards.experience} опыта, +{r.rewards.gold} золота")
            if r.rewards.loot: print("Добыча: " + self.describe(r.rewards.loot))
            if r.rewards.levels_gained > 0: print("Новый уровень!")

VIEW = ConsoleView()

def main():
    save_file = Path("saves") / "heroes.json"; game = GameFacade(save_file)
    hs = game.heroes
    if not hs: hero = create_hero(game)
    else:
        for i, h in enumerate(hs): print(f"{i+1} - {h.name}, {h.hero_class.display_name} {h.level} ур.")
        idx = read_choice(len(hs)); hero = hs[idx] if idx >= 0 else create_hero(game)
    print(f"{hero.name} разбивает лагерь.")
    while True:
        print(); VIEW.print_hero(hero)
        print("1 - в экспедицию, 2 - снаряжение, 3 - торговец, 4 - журнал, 0 - выход")
        c = input().strip()
        if c == "1":
            for i, l in enumerate(game.locations): print(f"{i+1} - {l.display_name} (ур. {l.recommended_level})")
            li = read_choice(len(game.locations))
            if li < 0: continue
            for i, t in enumerate(game.tactics): print(f"{i+1} - {t.display_name}: {t.description}")
            ti = read_choice(len(game.tactics))
            if ti < 0: continue
            r = game.explore(hero.name, game.locations[li].code, game.tactics[ti].code)
            print(); VIEW.print_report(r, game.locations[li].display_name)
        elif c == "2":
            if not hero.inventory: print("Пусто"); continue
            for i, i2 in enumerate(hero.inventory): print(f"{i+1} - {VIEW.describe(i2)}")
            idx = read_choice(len(hero.inventory))
            if idx >= 0: print("Экипировано:", VIEW.describe(game.equip(hero.name, idx)))
        elif c == "3":
            print("1 - купить, 2 - продать, 0 - назад"); c2 = input().strip()
            if c2 == "1":
                for i, i2 in enumerate(game.showcase): print(f"{i+1} - {VIEW.describe(i2)}: {i2.price}")
                idx = read_choice(len(game.showcase))
                if idx >= 0:
                    try: print("Куплено:", VIEW.describe(game.buy(hero.name, game.showcase[idx].code)))
                    except Exception as e: print(e)
            elif c2 == "2":
                if not hero.inventory: print("Пусто"); continue
                for i, i2 in enumerate(hero.inventory): print(f"{i+1} - {VIEW.describe(i2)}: {game.sell_price(i2)}")
                idx = read_choice(len(hero.inventory))
                if idx >= 0: print(f"Продано за {game.sell(hero.name, idx)}")
        elif c == "4":
            for r in game.get_journal(hero.name): print(f"{r.location_code}: {r.battle.outcome.name}")
        elif c == "0": break
        else: print("Нет такого варианта")

def create_hero(game):
    while True:
        for i, hc in enumerate(HeroClass):
            w, a = game.get_starter_kit(hc.code)
            print(f"{i+1} - {hc.display_name}: {VIEW.describe(w)}, {VIEW.describe(a)}")
        ci = read_choice(len(HeroClass))
        if ci < 0: continue
        name = input("Имя: ").strip()
        try: return game.create_hero(name, list(HeroClass)[ci].code)
        except ValueError as e: print(e)

def read_choice(c):
    try:
        c2 = int(input().strip())
        if 1 <= c2 <= c: return c2 - 1
    except: pass
    return -1

if __name__ == "__main__": main()