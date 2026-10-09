from animal import Animal


class Turtle(Animal):
    """Черепаха. Возраст: 1-й год = 15 чел., дальше по 2."""

    def __init__(self, name: str, age: int) -> None:
        super().__init__(name, age)

    def get_age_in_human_years(self) -> int:
        if self.get_age() <= 0:
            return 0
        return 15 + (self.get_age() - 1) * 2

    def express(self) -> None:
        print("""  _____     ____
 /      \\  |  o |
|        |/ ___\\|
|_________/
|_|_| |_|_|""")