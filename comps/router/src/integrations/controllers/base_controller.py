from abc import ABC, abstractmethod


class BaseController(ABC):
    """
    An abstract base controller class providing a framework for routing and 
    endpoint retrieval functionality.
    """

    @abstractmethod
    def route(self, messages, **kwargs):
        """
        Determines the appropriate routing based on input messages.
        """
        pass
