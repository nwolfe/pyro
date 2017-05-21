import tcod as libtcod


class UserInterface:
    def __init__(self, old_ui):
        self.screens = []
        self._old_ui = old_ui
        self._keybindings = {}

    def render_all(self, game):
        self._old_ui.render_all(game, False)

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

    def bind_key(self, key, input_):
        self._keybindings[key] = input_

    def push(self, screen, tag=None):
        screen.tag = tag
        screen.bind(self)
        self.screens.append(screen)
        self.render()

    def pop(self, result=None):
        screen = self.screens.pop()
        screen.unbind()
        self.screens[len(self.screens) - 1].activate(result, screen.tag)
        self.render()

    def refresh(self):
        for screen in self.screens:
            screen.update()
        # TODO Only render if dirty?
        self.render()

    def render(self):
        libtcod.console_clear(self.console)
        libtcod.console_clear(self.panel)

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
        libtcod.console_flush()

    def handle_input(self, key):
        screen = self.screens[len(self.screens) - 1]
        if key in self._keybindings:
            if screen.handle_input(self._keybindings[key]):
                return
        screen.handle_key_press(key)


class Screen:
    def __init__(self):
        self.ui = None
        self.transparent = False
        self.tag = None

    def bind(self, ui):
        self.ui = ui

    def unbind(self):
        self.ui = None

    def activate(self, result=None, tag=None):
        pass

    def update(self):
        pass

    def render(self):
        pass

    def handle_input(self, input_):
        return False

    def handle_key_press(self, key):
        pass
