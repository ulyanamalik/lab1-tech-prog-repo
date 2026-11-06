from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from .core import Combatant, EventType, Side, Outcome

class Action(Enum):
    ATTACK = (1.0, 1.0); POWER_STRIKE = (1.5, 1.5); DEFEND = (0.5, 0.3)
    def __init__(self, attack_multiplier: float, incoming_multiplier: float) -> None:
        self.attack_multiplier = attack_multiplier; self.incoming_multiplier = incoming_multiplier

class Tactic(ABC):
    @property
    @abstractmethod
    def code(self) -> str: ...
    @property
    @abstractmethod
    def display_name(self) -> str: ...
    @property
    @abstractmethod
    def description(self) -> str: ...
    @abstractmethod
    def choose_action(self, round: int, hero: Combatant, enemy: Combatant) -> Action: ...

class BalancedTactic(Tactic):
    @property
    def code(self) -> str: return "balanced"
    @property
    def display_name(self) -> str: return "Баланс"
    @property
    def description(self) -> str: return "обычный удар каждый раунд"
    def choose_action(self, round: int, hero: Combatant, enemy: Combatant) -> Action: return Action.ATTACK

class AggressiveTactic(Tactic):
    @property
    def code(self) -> str: return "aggressive"
    @property
    def display_name(self) -> str: return "Натиск"
    @property
    def description(self) -> str: return "безрассудные удары"
    def choose_action(self, round: int, hero: Combatant, enemy: Combatant) -> Action:
        return Action.POWER_STRIKE if enemy.health > hero.health else Action.ATTACK

class CautiousTactic(Tactic):
    @property
    def code(self) -> str: return "cautious"
    @property
    def display_name(self) -> str: return "Осторожность"
    @property
    def description(self) -> str: return "оборона при здоровье ниже 40%"
    def choose_action(self, round: int, hero: Combatant, enemy: Combatant) -> Action:
        return Action.DEFEND if hero.health < hero.max_health * 0.4 and round % 2 == 0 else Action.ATTACK

@dataclass(frozen=True)
class BattleEvent:
    round: int; type: EventType; source: Side; target: Side; amount: int; target_health_after: int

@dataclass(frozen=True)
class Participant:
    code: str; name: str; max_health: int
    @staticmethod
    def of(c) -> 'Participant': return Participant(c.code, c.name, c.max_health)

@dataclass(frozen=True)
class BattleReport:
    hero: Participant; enemy: Participant; outcome: Outcome; events: tuple[BattleEvent, ...]

class Battle:
    def __init__(self, hero: Combatant, enemy: Combatant, tactic: Tactic | None = None) -> None:
        self._hero = hero; self._enemy = enemy; self._tactic = tactic or BalancedTactic()
        self._events = []; self._round = 0
    def run(self) -> BattleReport:
        while self._hero.is_alive() and self._enemy.is_alive():
            self._round += 1
            action = self._tactic.choose_action(self._round, self._hero, self._enemy)
            if action == Action.POWER_STRIKE: self._emit(BattleEvent(self._round, EventType.POWER_STRIKE, Side.HERO, Side.ENEMY, 0, 0))
            elif action == Action.DEFEND: self._emit(BattleEvent(self._round, EventType.DEFEND, Side.HERO, Side.HERO, 0, 0))
            self._strike(self._hero, Side.HERO, self._enemy, Side.ENEMY, action.attack_multiplier)
            if self._enemy.is_alive(): self._strike(self._enemy, Side.ENEMY, self._hero, Side.HERO, action.incoming_multiplier)
        outcome = Outcome.VICTORY if self._hero.is_alive() else Outcome.DEFEAT
        return BattleReport(Participant.of(self._hero), Participant.of(self._enemy), outcome, tuple(self._events))
    def _strike(self, attacker, source, defender, target, multiplier):
        hit = attacker.roll_damage()
        damage = defender.receive_hit(max(1, round(hit.damage * multiplier)))
        if damage.evaded: self._emit(BattleEvent(self._round, EventType.EVADE, source, target, 0, defender.health)); return
        if damage.absorbed > 0: self._emit(BattleEvent(self._round, EventType.ABSORB, source, target, damage.absorbed, defender.health))
        if damage.amount > 0:
            et = EventType.CRITICAL_HIT if hit.critical else EventType.HIT
            self._emit(BattleEvent(self._round, et, source, target, damage.amount, defender.health))
        if not defender.is_alive(): self._emit(BattleEvent(self._round, EventType.DEATH, source, target, 0, 0))
    def _emit(self, event): self._events.append(event)