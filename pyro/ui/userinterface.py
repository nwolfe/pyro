import abc


class UserInterface:
    def __init__(self, old_ui):
        self.screens = []
        self._old_ui = old_ui

    @property
    def keyboard(self):
        return self._old_ui.keyboard

    @property
    def mouse(self):
        return self._old_ui.mouse

    @property
    def console(self):
        return self._old_ui.console

    @property
    def panel(self):
        return self._old_ui.panel

    def push(self, screen):
        screen.bind(self)
        self.screens.append(screen)
        self.render()

    def pop(self):
        screen = self.screens.pop()
        screen.unbind()
        active = self.screens[len(self.screens) - 1]
        active.activate()
        self.render()

    def refresh(self):
        for screen in self.screens:
            screen.update()
        # TODO Only render if dirty?
        self.render()

    def render(self):
        index = len(self.screens) - 1
        while index >= 0:
            if not self.screens[index].transparent:
                break
            index -= 1

        if index < 0:
            index = 0

        while index < len(self.screens):
            self.screens[index].render()
            index += 1

        # TODO reset dirty flag here
        # TODO move final call to console.flush() here?

    def handle_input(self):
        index = len(self.screens) - 1
        self.screens[index].handle_input()


class Screen:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.ui = None
        self.transparent = False

    def bind(self, ui):
        self.ui = ui

    def unbind(self):
        self.ui = None

    def activate(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def render(self):
        pass

    @abc.abstractmethod
    def handle_input(self):
        pass
