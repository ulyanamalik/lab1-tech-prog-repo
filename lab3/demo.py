from pathlib import Path
from tempfile import TemporaryDirectory
from .core import Dice, Damage, ArmorHandler, BarrierHandler, EvasionHandler, Outcome
from .items import create_default_catalog
from .characters import Hero, HeroClass, Goblin, Dragon, LegendaryEnemy, WindfuryEnemy, ArmoredEnemy, HauntedWeapon
from .combat import BalancedTactic, AggressiveTactic, CautiousTactic
from .world import Forest, Crypt, HauntedManor
from .game_systems import GameEventPublisher, GameEvent, GameEventType, AchievementTracker, ExpeditionJournal, FileHeroRepository, CachingHeroRepository, GameFacade
from .main import ConsoleView, VIEW

def new_hero(name, hero_class, level, catalog):
    return (Hero.Builder().set_name(name).set_hero_class(hero_class).set_starter_kit(hero_class.starter_kit(catalog)).set_level(level).build())

def print_hits(title, chain, count):
    results = []
    for _ in range(count):
        damage = Damage(30); chain.handle(damage)
        if damage.evaded: results.append("уклонение")
        elif damage.absorbed: results.append(f"поглощено {damage.absorbed}, прошло {damage.amount}")
        else: results.append(f"прошло {damage.amount}")
    print(title + ": " + "; ".join(results))

class EventPrinter:
    def on_event(self, event): print(f"Событие {event.type.name}: герой {event.hero.name}")

def main():
    catalog = create_default_catalog(); dice = Dice()
    print("===== Цепочка обязанностей =====")
    print_hits("Броня 30%", ArmorHandler(0.3), 2)
    chain = ArmorHandler(0.3); chain.set_next(BarrierHandler(30)); print_hits("Броня 30% -> барьер 30", chain, 3)
    dice.reseed(3); chain = EvasionHandler(0.5); chain.set_next(ArmorHandler(0.3)).set_next(BarrierHandler(30))
    print_hits("Уклонение 50% -> броня 30% -> барьер 30", chain, 3)
    print("\n===== Стратегия =====")
    for tactic in (BalancedTactic(), AggressiveTactic(), CautiousTactic()):
        mage = new_hero("Мерлин", HeroClass.MAGE, 2, catalog); report = Crypt(catalog).explore(mage, 9, tactic)
        result = "победа" if report.battle.outcome == Outcome.VICTORY else "поражение"
        print(f"{tactic.display_name}: {result}, раундов {report.battle.events[-1].round}, у героя осталось {mage.health}/{mage.max_health} здоровья")
    print("\n===== Декоратор =====")
    for enemy in (Goblin(), LegendaryEnemy(Goblin()), WindfuryEnemy(Goblin()), LegendaryEnemy(WindfuryEnemy(Goblin())), ArmoredEnemy(Goblin())):
        dice.reseed(5); hits = ", ".join(str(enemy.roll_damage().damage) for _ in range(3)); damage = enemy.receive_hit(20)
        print(f"{enemy.name}: удары {hits}, награда {enemy.experience_reward} опыта; входящий урон 20 -> {damage.amount}, здоровье {enemy.health}/{enemy.max_health}")
    print("\n===== Адаптер =====")
    bow = catalog.create_weapon("elven-bow"); enemy = HauntedWeapon(bow)
    print("Предмет: " + VIEW.describe(bow)); print(f"Враг: {enemy.name} ({enemy.max_health} здоровья, награда {enemy.experience_reward} опыта)")
    manor = HauntedManor(catalog); ranger = new_hero("Леголас", HeroClass.RANGER, 2, catalog)
    VIEW.print_report(manor.explore(ranger, 55, CautiousTactic()), manor.display_name)
    print("\n===== Наблюдатель =====")
    events = GameEventPublisher(); journal = ExpeditionJournal(); events.subscribe(GameEventType.VICTORY, AchievementTracker())
    events.subscribe(GameEventType.VICTORY, journal); events.subscribe(GameEventType.DEFEAT, journal); events.subscribe(GameEventType.VICTORY, EventPrinter())
    warrior = new_hero("Артур", HeroClass.WARRIOR, 1, catalog); report = Forest(catalog).explore(warrior, 7)
    result = GameEventType.VICTORY if report.battle.outcome == Outcome.VICTORY else GameEventType.DEFEAT
    events.publish(GameEvent(result, warrior, report))
    print("Достижения героя: " + ", ".join(a.display_name for a in warrior.achievements))
    print("Записей в журнале: " + str(len(journal.get_entries(warrior.name))))
    with TemporaryDirectory() as directory:
        print("\n===== Заместитель =====")
        save_file = Path(directory) / "heroes.json"; file = FileHeroRepository(save_file, catalog); file.save(warrior)
        print("Содержимое файла:"); print(save_file.read_text(encoding="utf-8"), end="")
        print("Без заместителя два поиска дают один и тот же объект:", file.find_by_name("Артур") is file.find_by_name("Артур"))
        cached = CachingHeroRepository(file); hero = cached.find_by_name("Артур")
        print("С заместителем два поиска дают один и тот же объект:", hero is cached.find_by_name("Артур"))
        hero.add_gold(100); cached.save(hero)
        print("После сохранения через заместитель золото героя в файле:", file.find_by_name("Артур").gold)
        print("\n===== Фасад =====")
        game = GameFacade(Path(directory) / "game.json"); game.create_hero("Гэндальф", "mage"); dice.reseed(11)
        report = game.explore("Гэндальф", "forest", "cautious")
        print(f"Экспедиция через фасад завершена: {report.battle.outcome.name}")
        VIEW.print_hero(game.get_hero("Гэндальф"))

if __name__ == "__main__": main()