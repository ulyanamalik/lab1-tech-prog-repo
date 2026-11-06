import copy
from dataclasses import dataclass
from abc import ABC, abstractmethod
from .core import Hit, Dice, UnknownCodeError

@dataclass(frozen=True)
class Enchantment:
    code: str; name: str; bonus_damage: int; bonus_defense: float; bonus_price: int

SHARP = Enchantment("sharp", "Острое", 3, 0, 20)
FIERY = Enchantment("fiery", "Огненное", 6, 0, 50)
STURDY = Enchantment("sturdy", "Прочное", 0, 0.05, 20)
WARDING = Enchantment("warding", "Охранное", 0, 0.10, 50)

def get_enchantment_by_code(code):
    for e in (SHARP, FIERY, STURDY, WARDING):
        if e.code == code: return e
    raise UnknownCodeError("Зачарование", code)

class Item(ABC):
    def __init__(self, code: str, name: str, base_price: int) -> None:
        self._code = code; self._name = name; self._base_price = base_price; self._enchantments = []
    def copy(self) -> 'Item':
        clone = copy.copy(self); clone._enchantments = list(self._enchantments); return clone
    @property
    @abstractmethod
    def possible_enchantments(self) -> tuple[Enchantment, ...]: ...
    @property
    @abstractmethod
    def description(self) -> str: ...
    def enchant(self, enchantment: Enchantment) -> None:
        if enchantment not in self.possible_enchantments: raise ValueError("Не подходит")
        self._enchantments.append(enchantment)
    @property
    def code(self) -> str: return self._code
    @property
    def name(self) -> str: return self._name
    @property
    def price(self) -> int: return self._base_price + sum(e.bonus_price for e in self._enchantments)
    @property
    def enchantments(self) -> tuple[Enchantment, ...]: return tuple(self._enchantments)

class Weapon(Item):
    def __init__(self, code: str, name: str, base_price: int, damage: int) -> None:
        super().__init__(code, name, base_price); self._damage = damage
    @abstractmethod
    def roll_damage(self) -> Hit: ...
    @property
    def damage(self) -> int: return self._damage + sum(e.bonus_damage for e in self.enchantments)
    @property
    def possible_enchantments(self) -> tuple[Enchantment, ...]: return (SHARP, FIERY)

class Sword(Weapon):
    def roll_damage(self) -> Hit: return Hit(self.damage, False)
    @property
    def description(self) -> str: return f"урон {self.damage}"

class Bow(Weapon):
    def __init__(self, code: str, name: str, base_price: int, damage: int, crit: float) -> None:
        super().__init__(code, name, base_price, damage); self._crit = crit
    def roll_damage(self) -> Hit: return Hit(self.damage * 2, True) if Dice().chance(self._crit) else Hit(self.damage, False)
    @property
    def description(self) -> str: return f"урон {self.damage}, крит {round(self._crit * 100)}%"

class Staff(Weapon):
    def __init__(self, code: str, name: str, base_price: int, damage: int, scatter: float) -> None:
        super().__init__(code, name, base_price, damage); self._scatter = scatter
    def roll_damage(self) -> Hit: return Hit(Dice().roll(self._min_dmg, self._max_dmg), False)
    @property
    def description(self) -> str: return f"урон {self._min_dmg}-{self._max_dmg}"
    @property
    def _min_dmg(self) -> int: return round(self.damage * (1 - self._scatter))
    @property
    def _max_dmg(self) -> int: return round(self.damage * (1 + self._scatter))

class Armor(Item):
    def __init__(self, code: str, name: str, base_price: int, defense: float) -> None:
        super().__init__(code, name, base_price); self._defense = defense
    @property
    def defense(self) -> float: return min(0.75, self._defense + sum(e.bonus_defense for e in self.enchantments))
    @property
    def possible_enchantments(self) -> tuple[Enchantment, ...]: return (STURDY, WARDING)
    @property
    def description(self) -> str: return f"защита {round(self.defense * 100)}%"

class ItemCatalog:
    def __init__(self) -> None: self._prototypes = {}
    def register(self, prototype: Item) -> None: self._prototypes[prototype.code] = prototype
    def create(self, code: str) -> Item:
        if code not in self._prototypes: raise UnknownCodeError("Предмет", code)
        return self._prototypes[code].copy()
    def create_weapon(self, code: str) -> Weapon:
        item = self.create(code)
        if isinstance(item, Weapon): return item
        raise ValueError("Не оружие")
    def create_armor(self, code: str) -> Armor:
        item = self.create(code)
        if isinstance(item, Armor): return item
        raise ValueError("Не броня")

def create_default_catalog() -> ItemCatalog:
    c = ItemCatalog()
    c.register(Sword("training-sword", "Тренировочный меч", 20, 12))
    c.register(Bow("hunting-bow", "Охотничий лук", 20, 10, 0.3))
    c.register(Staff("apprentice-staff", "Посох ученика", 20, 14, 0.3))
    c.register(Armor("chainmail", "Кольчуга", 40, 0.3))
    c.register(Armor("leather-armor", "Кожаная броня", 30, 0.2))
    c.register(Armor("linen-robe", "Льняная роба", 15, 0.1))
    c.register(Sword("iron-sword", "Железный меч", 80, 17))
    c.register(Bow("elven-bow", "Эльфийский лук", 90, 14, 0.4))
    c.register(Staff("ember-staff", "Тлеющий посох", 90, 20, 0.3))
    c.register(Armor("plate-armor", "Латы", 120, 0.4))
    c.register(Sword("goblin-cleaver", "Гоблинский тесач", 40, 15))
    c.register(Bow("bone-bow", "Костяной лук", 140, 17, 0.4))
    c.register(Staff("necromancer-staff", "Посох некроманта", 150, 25, 0.35))
    c.register(Sword("knight-blade", "Клинок рыцаря", 150, 23))
    c.register(Armor("crypt-mail", "Кольчуга стража склепа", 160, 0.45))
    c.register(Sword("dawn-blade", "Клинок рассвета", 500, 35))
    c.register(Armor("dragonscale-armor", "Драконья чешуя", 500, 0.55))
    return c

class StarterKitFactory(ABC):
    @abstractmethod
    def create_weapon(self) -> Weapon: ...
    @abstractmethod
    def create_armor(self) -> Armor: ...

class WarriorKitFactory(StarterKitFactory):
    def __init__(self, catalog: ItemCatalog): self._cat = catalog
    def create_weapon(self) -> Weapon: return self._cat.create_weapon("training-sword")
    def create_armor(self) -> Armor: return self._cat.create_armor("chainmail")

class RangerKitFactory(StarterKitFactory):
    def __init__(self, catalog: ItemCatalog): self._cat = catalog
    def create_weapon(self) -> Weapon: return self._cat.create_weapon("hunting-bow")
    def create_armor(self) -> Armor: return self._cat.create_armor("leather-armor")

class MageKitFactory(StarterKitFactory):
    def __init__(self, catalog: ItemCatalog): self._cat = catalog
    def create_weapon(self) -> Weapon: return self._cat.create_weapon("apprentice-staff")
    def create_armor(self) -> Armor: return self._cat.create_armor("linen-robe")