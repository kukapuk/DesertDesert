class World:
    def __init__(self):
        self._next_id = 0
        self._components = {}

    def create_entity(self) -> int:
        eid = self._next_id
        self._next_id += 1
        self._components[eid] = {}
        return eid

    def add_component(self, eid: int, name: str, data):
        self._components[eid][name] = data

    def get_component(self, eid: int, name: str):
        return self._components[eid].get(name)

    def get_entities_with(self, *names) -> list:
        result = []
        for eid, comps in self._components.items():
            if all(n in comps for n in names):
                result.append(eid)
        return result

    def destroy_entity(self, eid: int):
        self._components.pop(eid, None)

    def clear_level(self, keep: list = None):
        keep = keep or []
        to_remove = [e for e in self._components if e not in keep]
        for eid in to_remove:
            self.destroy_entity(eid)
