from lab3.characters import Hero, HeroClass, Achievement
from lab3.items import create_default_catalog
from lab3.game_systems import FileHeroRepository

def test_restores_hero_through_new_repository(tmp_path):
    catalog = create_default_catalog()
    file = tmp_path / "heroes.json"
    writer = FileHeroRepository(file, catalog)
    original = (Hero.Builder().set_name("Артур").set_hero_class(HeroClass.WARRIOR)
                .set_starter_kit(HeroClass.WARRIOR.starter_kit(catalog))
                .set_level(2).set_experience(35).set_gold(175)
                .set_achievements([Achievement.FIRST_BLOOD]).build())

    writer.save(original)
    reader = FileHeroRepository(file, create_default_catalog())
    restored = reader.find_by_name("Артур")

    assert restored is not None
    assert restored is not original
    assert restored.name == "Артур"
    assert restored.hero_class == HeroClass.WARRIOR
    assert restored.level == 2
    assert restored.experience == 35
    assert restored.gold == 175
    assert restored.weapon.code == original.weapon.code
    assert restored.armor.code == original.armor.code
    assert restored.achievements == (Achievement.FIRST_BLOOD,)

def test_missing_file_means_empty_storage(tmp_path):
    repository = FileHeroRepository(tmp_path / "missing.json", create_default_catalog())
    assert repository.find_all() == []
    assert repository.find_by_name("Артур") is None