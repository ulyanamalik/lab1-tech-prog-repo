from enum import Enum
from abc import abstractmethod
from .core import Combatant, Hit, Damage, Dice, ArmorHandler, BarrierHandler, EvasionHandler, UnknownCodeError
from .items import Weapon, Armor, Item, WarriorKitFactory, RangerKitFactory, MageKitFactory

class Achievement(Enum):
    FIRST_BLOOD = ("first-blood", "Первая кровь")
    LUCKY = ("lucky", "Счастливчик")
    VETERAN = ("veteran", "Ветеран")
    DRAGON_SLAYER = ("dragon-slayer", "Драконоборец")
    def __init__(self, code, display_name): self.code = code; self.display_name = display_name
    @classmethod
    def by_code(cls, code):
        for a in cls:
            if a.code == code: return a
        raise ValueError("Нет ачивки")

class HeroClass(Enum):
    WARRIOR = ("warrior", "Воин", 120, WarriorKitFactory)
    RANGER = ("ranger", "Следопыт", 100, RangerKitFactory)
    MAGE = ("mage", "Маг", 85, MageKitFactory)
    def __init__(self, code, display_name, base_health, factory_cls):
        self.code = code; self.display_name = display_name; self.base_health = base_health; self._factory_cls = factory_cls
    def starter_kit(self, catalog): return self._factory_cls(catalog)
    @classmethod
    def by_code(cls, code):
        for hc in cls:
            if hc.code == code: return hc
        raise UnknownCodeError("Класс", code)
    def create_defense(self, armor, level):
        evasion = 0.15 if self == HeroClass.RANGER else 0.0
        barrier = 30 if self == HeroClass.MAGE else 0
        if self == HeroClass.WARRIOR and level >= 3: barrier = 20
        elif self == HeroClass.RANGER and level >= 5: barrier = 15
        elif self == HeroClass.MAGE and level >= 3: evasion = 0.10
        armor_h = ArmorHandler(armor.defense)
        first = armor_h
        if evasion > 0: first = EvasionHandler(evasion); first.set_next(armor_h)
        if barrier > 0: armor_h.set_next(BarrierHandler(barrier))
        return first

class Hero(Combatant):
    def __init__(self, builder: 'Hero.Builder') -> None:
        self._name = builder.name; self._hero_class = builder.hero_class
        self._level = builder.level; self._experience = builder.experience
        self._gold = builder.gold; self._weapon = builder.weapon; self._armor = builder.armor
        self._inventory = list(builder.inventory); self._achievements = list(dict.fromkeys(builder.achievements))
        self.rest()
    class Builder:
        def __init__(self):
            self.name=None; self.hero_class=None; self.weapon=None; self.armor=None
            self.level=1; self.gold=50; self.experience=0; self.inventory=[]; self.achievements=[]
        def set_name(self, n): self.name=n; return self
        def set_hero_class(self, hc): self.hero_class=hc; return self
        def set_weapon(self, w): self.weapon=w; return self
        def set_armor(self, a): self.armor=a; return self
        def set_starter_kit(self, kit): self.weapon=kit.create_weapon(); self.armor=kit.create_armor(); return self
        def set_level(self, l): self.level=l; return self
        def set_gold(self, g): self.gold=g; return self
        def set_experience(self, e): self.experience=e; return self
        def set_inventory(self, i): self.inventory=i; return self
        def set_achievements(self, a): self.achievements=a; return self
        def build(self):
            if not self.name or not self.name.strip(): raise ValueError("Нужно имя")
            if not self.hero_class: raise ValueError("Нужен класс")
            if not self.weapon or not self.armor: raise ValueError("Нужно снаряжение")
            return Hero(self)
    def roll_damage(self): return Hit(self._weapon.roll_damage().damage + (self._level-1)*3, False)
    def receive_hit(self, amount):
        d = Damage(amount); self._defense.handle(d); self._health = max(0, self._health - d.amount); return d
    def is_alive(self): return self._health > 0
    def rest(self): self._health = self.max_health; self._defense = self._hero_class.create_defense(self._armor, self._level)
    def gain_experience(self, amount):
        self._experience += amount; lg = 0
        while self._experience >= self._level*100: self._experience -= self._level*100; self._level += 1; lg += 1
        return lg
    def add_gold(self, amount): self._gold += amount
    def spend_gold(self, amount):
        if amount > self._gold: raise ValueError("Мало золота")
        self._gold -= amount
    def add_item(self, item): self._inventory.append(item)
    def remove_item(self, item):
        if item not in self._inventory: raise ValueError("Нет предмета")
        self._inventory.remove(item)
    def equip(self, item):
        if isinstance(item, Weapon): self.remove_item(item); self._inventory.append(self._weapon); self._weapon = item
        elif isinstance(item, Armor): self.remove_item(item); self._inventory.append(self._armor); self._armor = item; self._defense = self._hero_class.create_defense(self._armor, self._level)
    def unlock(self, ach):
        if ach in self._achievements: return False
        self._achievements.append(ach); return True
    @property
    def code(self): return self._hero_class.code
    @property
    def name(self): return self._name
    @property
    def health(self): return self._health
    @property
    def max_health(self): return self._hero_class.base_health + (self._level-1)*15
    @property
    def hero_class(self): return self._hero_class
    @property
    def level(self): return self._level
    @property
    def experience(self): return self._experience
    @property
    def experience_to_next_level(self): return self._level * 100
    @property
    def gold(self): return self._gold
    @property
    def weapon(self): return self._weapon
    @property
    def armor(self): return self._armor
    @property
    def inventory(self): return tuple(self._inventory)
    @property
    def achievements(self): return tuple(self._achievements)

class Enemy(Combatant):
    @property
    @abstractmethod
    def experience_reward(self) -> int: ...
    @abstractmethod
    def roll_gold_reward(self) -> int: ...

class AbstractEnemy(Enemy):
    def __init__(self, code, name, hp, min_d, max_d, exp, gold, defense=None):
        self._code=code; self._name=name; self._max_health=hp; self._min_d=min_d; self._max_d=max_d
        self._exp=exp; self._gold=gold; self._health=hp; self._defense=defense
    def roll_damage(self): return Hit(Dice().roll(self._min_d, self._max_d), False)
    def receive_hit(self, amount):
        d = Damage(amount)
        if self._defense: self._defense.handle(d)
        self._health = max(0, self._health - d.amount); return d
    def is_alive(self): return self._health > 0
    def roll_gold_reward(self): return Dice().roll(self._gold//2, self._gold)
    @property
    def experience_reward(self): return self._exp
    @property
    def code(self): return self._code
    @property
    def name(self): return self._name
    @property
    def health(self): return self._health
    @property
    def max_health(self): return self._max_health

class Goblin(AbstractEnemy):
    def __init__(self): super().__init__("goblin", "Гоблин", 50, 6, 14, 40, 30)

class Skeleton(AbstractEnemy):
    def __init__(self): super().__init__("skeleton", "Скелет", 110, 10, 24, 90, 70, ArmorHandler(0.3))

class Dragon(AbstractEnemy):
    def __init__(self): super().__init__("dragon", "Дракон", 260, 16, 22, 500, 400, ArmorHandler(0.25))
    def roll_damage(self):
        bite = super().roll_damage()
        return Hit(bite.damage*2, True) if Dice().chance(0.25) else bite

class HauntedWeapon(Enemy):
    def __init__(self, w): self._w=w; self._max_health=w.damage*5; self._health=self._max_health
    @property
    def code(self): return "haunted-weapon"
    @property
    def name(self): return "Одержимый " + self._w.name
    @property
    def health(self): return self._health
    @property
    def max_health(self): return self._max_health
    def is_alive(self): return self._health > 0
    def roll_damage(self): return self._w.roll_damage()
    def receive_hit(self, amount):
        d = Damage(amount); self._health = max(0, self._health - d.amount); return d
    @property
    def experience_reward(self): return self._w.price // 2
    def roll_gold_reward(self): return Dice().roll(self._w.price//4, self._w.price//2)

class EnemyDecorator(Enemy):
    def __init__(self, wrapped: Enemy): self._w = wrapped
    @property
    def code(self): return self._w.code
    @property
    def name(self): return self._w.name
    @property
    def health(self): return self._w.health
    @property
    def max_health(self): return self._w.max_health
    @property
    def experience_reward(self): return self._w.experience_reward
    def is_alive(self): return self._w.is_alive()
    def roll_damage(self): return self._w.roll_damage()
    def receive_hit(self, amount): return self._w.receive_hit(amount)
    def roll_gold_reward(self): return self._w.roll_gold_reward()

class LegendaryEnemy(EnemyDecorator):
    @property
    def name(self): return "Легендарный " + super().name
    def roll_damage(self):
        hit = super().roll_damage(); return Hit(hit.damage*2, hit.critical)
    @property
    def experience_reward(self): return super().experience_reward * 2
    def roll_gold_reward(self): return super().roll_gold_reward() * 2

class WindfuryEnemy(EnemyDecorator):
    @property
    def name(self): return "Неистовый " + super().name
    def roll_damage(self):
        f, s = super().roll_damage(), super().roll_damage()
        return Hit(f.damage+s.damage, f.critical or s.critical)
    @property
    def experience_reward(self): r = super().experience_reward; return r + r//2
    def roll_gold_reward(self): r = super().roll_gold_reward(); return r + r//2

class ArmoredEnemy(EnemyDecorator):
    @property
    def name(self): return "Бронированный " + super().name
    def receive_hit(self, amount): return super().receive_hit(amount - amount//2) if amount > 0 else Damage(0)