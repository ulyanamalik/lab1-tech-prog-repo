class Enemy:
    def __init__(self, name):
        self.name = name

# Абстрактный создатель
class Location:
    def explore(self):
        enemy = self.create_enemy()
        print(f"Исследуем локацию, встречаем врага: {enemy.name}")

    def create_enemy(self):
        raise NotImplementedError

# Конкретный создатель 1
class Forest(Location):
    def create_enemy(self):
        return Enemy("Гоблин")

# Конкретный создатель 2
class DragonLair(Location):
    def create_enemy(self):
        return Enemy("Дракон")