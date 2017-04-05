

class Entity:
    def __init__(self, components=None):
        self.components = {}
        if components:
            for comp in components:
                self.set_component(comp)

    def component(self, component_type):
        return self.components.get(component_type)

    def set_component(self, component):
        self.remove_component(component.type)
        self.components[component.type] = component
        component.set_owner(self)

    def remove_component(self, component_type):
        if component_type in self.components:
            self.components.pop(component_type)
