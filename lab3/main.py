from dice import Dice
from items import Item
from builder import Hero
from abstract_factory import WarriorKitFactory, RangerKitFactory
from factory_method import Forest, DragonLair

def main():
    print("===== Одиночка (Singleton) =====")
    dice1 = Dice()
    dice2 = Dice()
    print(f"dice1 is dice2: {dice1 is dice2}")
    print(f"Бросок кости: {dice1.roll(1, 6)}")
    
    print("\n===== Прототип (Prototype) =====")
    base_sword = Item("Железный меч", 17)
    sword_copy = base_sword.copy()
    sword_copy.enchant("Огненное")
    print(f"Оригинал: {base_sword}")
    print(f"Копия:    {sword_copy}")
    print(f"Это разные объекты: {base_sword is not sword_copy}")

    print("\n===== Абстрактная фабрика (Abstract Factory) =====")
    warrior_kit = WarriorKitFactory()
    ranger_kit = RangerKitFactory()
    print(f"Воин получает: {warrior_kit.create_weapon()} и {warrior_kit.create_armor()}")
    print(f"Следопыт получает: {ranger_kit.create_weapon()} и {ranger_kit.create_armor()}")

    print("\n===== Строитель (Builder) =====")
    hero = (Hero.Builder()
            .set_name("Артур")
            .set_hero_class("Воин")
            .set_level(3)
            .set_starter_kit(warrior_kit)
            .build())
    print(f"Создан герой: {hero}")
    try:
        Hero.Builder().set_hero_class("Маг").build()
    except ValueError as e:
        print(f"Ошибка при создании: {e}")

    print("\n===== Фабричный метод (Factory Method) =====")
    forest = Forest()
    lair = DragonLair()
    forest.explore()
    lair.explore()

if __name__ == "__main__":
    main()