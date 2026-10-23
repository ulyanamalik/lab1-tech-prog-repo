import random

class Dice:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Dice, cls).__new__(cls)
            cls._instance.random = random.Random()
        return cls._instance

    def roll(self, min_val, max_val):
        return self.random.randint(min_val, max_val)