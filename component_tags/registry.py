class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class ComponentRegistry(object):
    def __init__(self):
        self._registry = {}  # component name -> component_class mapping

    def register(self, component):
        name = component.name
        if not name in self._registry:
            self._registry[name] = component

    def clear(self):
        self._registry = {}
