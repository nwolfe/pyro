

class EventListener:
    def __init__(self):
        pass

    def handle_event(self, event, context):
        pass


class EventSource:
    def __init__(self):
        self.listeners = None

    def fire_event(self, event, context):
        if self.listeners:
            for listener in self.listeners:
                listener.handle_event(event, context)

    def add_event_listener(self, listener):
        if self.listeners is None:
            self.listeners = []
        self.listeners.append(listener)

    def remove_event_listener(self, listener):
        if self.listeners:
            self.listeners.remove(listener)
