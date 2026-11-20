from unittest.mock import create_autospec
from lab3.characters import Hero, HeroClass
from lab3.items import create_default_catalog
from lab3.game_systems import CachingHeroRepository, FileHeroRepository

def warrior(name):
    return (Hero.Builder().set_name(name).set_hero_class(HeroClass.WARRIOR)
            .set_starter_kit(HeroClass.WARRIOR.starter_kit(create_default_catalog())).build())

def test_loads_lazily():
    storage = create_autospec(FileHeroRepository, instance=True)
    CachingHeroRepository(storage)
    assert storage.mock_calls == []

def test_reads_storage_only_once():
    storage = create_autospec(FileHeroRepository, instance=True)
    hero = warrior("Артур")
    storage.find_all.return_value = [hero]
    cache = CachingHeroRepository(storage)

    first = cache.find_by_name("Артур")
    second = cache.find_by_name("Артур")

    assert first is hero
    assert second is first
    storage.find_all.assert_called_once_with()

def test_saves_to_storage_and_updates_cache():
    storage = create_autospec(FileHeroRepository, instance=True)
    old_hero = warrior("Артур")
    storage.find_all.return_value = [old_hero]
    cache = CachingHeroRepository(storage)
    assert cache.find_by_name("Артур") is old_hero
    updated = warrior("Артур")
    updated.add_gold(100)

    cache.save(updated)

    storage.save.assert_called_once_with(updated)
    assert cache.find_by_name("Артур") is updated
    storage.find_all.assert_called_once_with()