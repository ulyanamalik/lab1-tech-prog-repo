class Hero:
    def __init__(self, builder):
        self.name = builder.name
        self.hero_class = builder.hero_class
        self.level = builder.level
        self.weapon = builder.weapon
        self.armor = builder.armor

    def __str__(self):
        return f"{self.name}, {self.hero_class} {self.level} ур. | Оружие: {self.weapon} | Броня: {self.armor}"

    class Builder:
        def __init__(self):
            self.name = None
            self.hero_class = None
            self.level = 1
            self.weapon = None
            self.armor = None

        def set_name(self, name):
            self.name = name
            return self

        def set_hero_class(self, hero_class):
            self.hero_class = hero_class
            return self

        def set_level(self, level):
            self.level = level
            return self

        def set_starter_kit(self, kit):
            self.weapon = kit.create_weapon()
            self.armor = kit.create_armor()
            return self

        def build(self):
            if not self.name:
                raise ValueError("У героя должно быть имя")
            if not self.hero_class:
                raise ValueError("Не выбран класс героя")
            if not self.weapon or not self.armor:
                raise ValueError("Герою нужны оружие и броня")
            return Hero(self)