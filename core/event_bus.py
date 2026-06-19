class EventBus:
    def __init__(self):
        self._listeners = {}

    def subscribe(self, event_type: str, fn):
        self._listeners.setdefault(event_type, []).append(fn)

    def unsubscribe(self, event_type: str, fn):
        if event_type in self._listeners:
            self._listeners[event_type].remove(fn)

    def publish(self, event_type: str, data=None):
        for fn in self._listeners.get(event_type, []):
            fn(data)
