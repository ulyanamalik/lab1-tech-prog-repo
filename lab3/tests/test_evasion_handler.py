from unittest.mock import create_autospec, patch
from lab3.core import Dice, Damage, DamageHandler, EvasionHandler

def test_evades_and_stops_chain():
    dice = create_autospec(Dice, instance=True)
    dice.chance.return_value = True
    next_handler = create_autospec(DamageHandler, instance=True)
    handler = EvasionHandler(0.3)
    handler.set_next(next_handler)
    damage = Damage(40)

    with patch("lab3.core.Dice", return_value=dice) as singleton:
        handler.handle(damage)
        singleton.assert_called_once_with()

    assert damage.amount == 0
    assert damage.evaded is True
    dice.chance.assert_called_once_with(0.3)
    assert next_handler.mock_calls == []

def test_forwards_damage_when_roll_fails():
    dice = create_autospec(Dice, instance=True)
    dice.chance.return_value = False
    next_handler = create_autospec(DamageHandler, instance=True)
    handler = EvasionHandler(0.3)
    handler.set_next(next_handler)
    damage = Damage(40)

    with patch("lab3.core.Dice", return_value=dice):
        handler.handle(damage)

    assert damage.amount == 40
    assert damage.evaded is False
    next_handler.handle.assert_called_once_with(damage)