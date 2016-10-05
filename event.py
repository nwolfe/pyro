

class EventHandler:
    def handle_event(self, event, data):
        return


class EventEmitter:
    def __init__(self):
        self.event_handlers = dict()

    def fire_event(event, data=None):
        if self.event_handlers.has_key(event):
            if data is None:
                data = dict()
            for handler in self.event_handlers[event]:
                handler.handle_event(event, data)

    def add_event_handler(handler, *events):
        for event in events:
            if self.event_handlers.has_key(event):
                self.event_handlers[event].append(handler)
            else:
                handlers = list(handler)
                self.event_handlers[event] = handlers
