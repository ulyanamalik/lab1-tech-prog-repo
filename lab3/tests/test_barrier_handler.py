import pytest
from lab3.core import BarrierHandler, Damage

def damage_cases():
    return [(0, 0, 0), (10, 10, 0), (30, 30, 0), (40, 30, 10)]

@pytest.mark.parametrize("incoming, absorbed, remaining", damage_cases())
def test_handles_damage_boundaries(incoming, absorbed, remaining):
    barrier = BarrierHandler(30)
    damage = Damage(incoming)
    barrier.handle(damage)
    assert damage.absorbed == absorbed
    assert damage.amount == remaining

def test_spends_capacity_across_hits():
    barrier = BarrierHandler(30)
    first, second, third = Damage(20), Damage(20), Damage(20)
    barrier.handle(first)
    barrier.handle(second)
    barrier.handle(third)
    assert (first.absorbed, first.amount) == (20, 0)
    assert (second.absorbed, second.amount) == (10, 10)
    assert (third.absorbed, third.amount) == (0, 20)