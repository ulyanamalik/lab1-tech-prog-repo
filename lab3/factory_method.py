class Enemy:
    def __init__(self, name, health, damage):
        self.name = name
        self.health = health
        self.damage = damage

# Абстрактный создатель (базовая локация)
class Location:
    def explore(self, hero):
        # Вызываем фабричный метод, который создаст врага
        enemy = self.create_enemy()
        print(f"\nГерой {hero.name} отправляется в локацию {self.__class__.__name__}...")
        print(f"Встречен враг: {enemy.name} (Здоровье: {enemy.health})")
        
        # Простая имитация боя
        while enemy.health > 0:
            # Берем урон из оружия героя (hero.weapon.value)
            damage = hero.weapon.value
            enemy.health -= damage
            print(f"  [Бой] {hero.name} наносит удар на {damage} урона! У врага осталось: {max(0, enemy.health)} HP.")
        
        print(f"  [Победа] {enemy.name} повержен! Герой получает 50 золота.")
        return 50

    # Это и есть фабричный метод, который переопределяют наследники
    def create_enemy(self):
        raise NotImplementedError

# Конкретный создатель 1 (Лес)
class Forest(Location):
    def create_enemy(self):
        return Enemy("Гоблин", 30, 5)

# Конкретный создатель 2 (Логово)
class DragonLair(Location):
    def create_enemy(self):
        return Enemy("Дракон", 100, 20)