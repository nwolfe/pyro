import abc


class Screen:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def render(self):
        pass
