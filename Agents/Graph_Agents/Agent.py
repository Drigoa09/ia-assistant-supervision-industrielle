from abc import ABC, abstractmethod
from OrderState import OrderState

class Agent(ABC):

    @abstractmethod
    def interaction(self, State : OrderState) -> OrderState:
        pass

    def obtenir_tokens(self, data_caracs):
        return (data_caracs.usage_metadata['input_tokens'], data_caracs.usage_metadata['output_tokens'])

