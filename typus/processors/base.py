from abc import ABC, abstractmethod
from typing import Type

from typus.core import TypusCore


class BaseProcessor(ABC):
    """
    Processors are the workers of Typus. See subclasses for examples.
    """

    other: 'BaseProcessor' = None

    def __init__(self, typus: TypusCore):
        # Stores Typus to access it's configuration
        self.typus = typus

    def __radd__(self, other: Type['BaseProcessor']):
        self.other = other
        return self

    @abstractmethod
    def run(self, text: str, **kwargs) -> str:
        """
        :param text: Input text
        :param kwargs: Optional settings for the current call
        :return: Output text
        """

    def run_other(self, text: str, **kwargs) -> str:
        if self.other:
            return self.other.run(text, **kwargs)
        return text
