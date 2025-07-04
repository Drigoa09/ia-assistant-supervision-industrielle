from abc import ABC, abstractmethod
from OrderState import OrderState

class Agent(ABC):

    @abstractmethod
    def interaction(self, State : OrderState) -> OrderState:
        pass
