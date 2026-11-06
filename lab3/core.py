import random
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from typing import Sequence, TypeVar

T = TypeVar("T")

class UnknownCodeError(LookupError):
    def __init__(self, what: str, code: str) -> None:
        super().__init__(f"{what} с кодом '{code}' не существует")

class Dice:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._random = random.Random()
        return cls._instance
    def reseed(self, seed: int) -> None: self._random.seed(seed)
    def next_seed(self) -> int: return self._random.randrange(1_000_000)
    def roll(self, low: int, high: int) -> int: return self._random.randint(low, high)
    def chance(self, probability: float) -> bool: return self._random.random() < probability
    def pick(self, options: Sequence[T]) -> T: return self._random.choice(options)

@dataclass(frozen=True)
class Hit:
    damage: int
    critical: bool

@dataclass
class Damage:
    amount: int
    evaded: bool = False
    absorbed: int = 0
    def reduce_to(self, amount: int) -> None: self.amount = amount
    def evade(self) -> None: self.amount = 0; self.evaded = True
    def absorb(self, value: int) -> None: self.amount -= value; self.absorbed += value

class Side(Enum): HERO = "hero"; ENEMY = "enemy"
class Outcome(Enum): VICTORY = "victory"; DEFEAT = "defeat"

class EventType(Enum):
    HIT = "hit"; CRITICAL_HIT = "critical_hit"; DEATH = "death"
    POWER_STRIKE = "power-strike"; DEFEND = "defend"; EVADE = "evade"; ABSORB = "absorb"

class Combatant(ABC):
    @property
    @abstractmethod
    def code(self) -> str: ...
    @property
    @abstractmethod
    def name(self) -> str: ...
    @property
    @abstractmethod
    def health(self) -> int: ...
    @property
    @abstractmethod
    def max_health(self) -> int: ...
    @abstractmethod
    def is_alive(self) -> bool: ...
    @abstractmethod
    def roll_damage(self) -> Hit: ...
    @abstractmethod
    def receive_hit(self, damage: int) -> Damage: ...

class DamageHandler(ABC):
    def __init__(self) -> None: self._next = None
    def set_next(self, handler: 'DamageHandler') -> 'DamageHandler': self._next = handler; return handler
    @abstractmethod
    def handle(self, damage: Damage) -> None: ...
    def _pass_to_next(self, damage: Damage) -> None:
        if self._next is not None: self._next.handle(damage)

class EvasionHandler(DamageHandler):
    def __init__(self, chance: float) -> None: super().__init__(); self._chance = chance
    def handle(self, damage: Damage) -> None:
        if Dice().chance(self._chance): damage.evade(); return
        self._pass_to_next(damage)

class ArmorHandler(DamageHandler):
    def __init__(self, defense: float) -> None: super().__init__(); self._defense = defense
    def handle(self, damage: Damage) -> None:
        damage.reduce_to(max(1, round(damage.amount * (1 - self._defense)))); self._pass_to_next(damage)

class BarrierHandler(DamageHandler):
    def __init__(self, strength: int) -> None: super().__init__(); self._strength = strength
    def handle(self, damage: Damage) -> None:
        absorbed = min(self._strength, damage.amount)
        if absorbed > 0: self._strength -= absorbed; damage.absorb(absorbed)
        self._pass_to_next(damage)