import copy

class Item:
    def __init__(self, name, value, stat_type="урон"):
        self.name = name
        self.value = value
        self.stat_type = stat_type  # "урон" для оружия, "защита" для брони
        self.enchantments = []

    def enchant(self, enchantment):
        self.enchantments.append(enchantment)

    def copy(self):
        return copy.deepcopy(self)

    def __str__(self):
        ench = f" [{', '.join(self.enchantments)}]" if self.enchantments else ""
        return f"{self.name}{ench} ({self.stat_type} {self.value})"