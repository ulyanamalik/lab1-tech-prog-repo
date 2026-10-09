from abc import ABC, abstractmethod


class Pet(ABC):
    """Абстрактный питомец. Задаёт контракт для всех животных."""

    @abstractmethod
    def express(self) -> None:
        """Показать, как животное выражает себя."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Вернуть кличку."""
        pass

    @abstractmethod
    def get_age(self) -> int:
        """Вернуть возраст в годах животного."""
        pass

    @abstractmethod
    def get_age_in_human_years(self) -> int:
        """Вернуть возраст в человеческих годах."""
        pass