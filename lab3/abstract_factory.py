from items import Item

class Weapon(Item):
    pass

class Armor(Item):
    def __init__(self, name, defense):
        super().__init__(name, defense, stat_type="защита")

# Абстрактная фабрика
class StarterKitFactory:
    def create_weapon(self):
        raise NotImplementedError

    def create_armor(self):
        raise NotImplementedError

# Конкретная фабрика 1
class WarriorKitFactory(StarterKitFactory):
    def create_weapon(self):
        return Weapon("Тренировочный меч", 12)
    
    def create_armor(self):
        return Armor("Кольчуга", 30)

# Конкретная фабрика 2
class RangerKitFactory(StarterKitFactory):
    def create_weapon(self):
        return Weapon("Охотничий лук", 10)
    
    def create_armor(self):
        return Armor("Кожаная броня", 20)