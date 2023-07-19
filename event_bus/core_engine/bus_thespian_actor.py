from thespian.actors import *
from typing import Callable, Any

class EventMessage(object):
    def __init__(self, event: str, *args, **kwargs):
        self.event = event
        self.args = args
        self.kwargs = kwargs

class EventActor(Actor):
    def __init__(self):
        self._events = defaultdict(set)

    def receiveMessage(self, message: Any, sender: ActorAddress) -> None:
        """Process incoming messages from other actors.

        Args:
            message: The received message.
            sender: The address of the sender.

        """
        if isinstance(message, EventMessage):
            self.emit(message.event, *message.args, **message.kwargs)

    def add_event(self, func: Callable, event: str) -> None:
        """Adds a function to an event.

        Args:
            func: The function to call when the event is emitted.
            event: Name of the event.

        """
        self._events[event].add(func)

    def emit(self, event: str, *args, **kwargs) -> None:
        """Emits an event and runs the subscribed functions.

        Args:
            event: Name of the event.

        """
        if event in self._events:
            for func in self._events[event]:
                func(*args, **kwargs)

    def remove_event(self, func_name: str, event: str) -> None:
        """Removes a subscribed function from a specific event.

        Args:
            func_name: The name of the function to be removed.
            event: The name of the event.

        """
        self._events[event] = {func for func in self._events[event] if func.__name__ != func_name}

class EventBus:
    def __init__(self):
        self._actor_system = ActorSystem("multiprocQueueBase")

    def on(self, event: str) -> Callable:
        """Decorator for subscribing a function to a specific event.

        Args:
            event: Name of the event to subscribe to.

        Returns:
            The outer function.

        """
        def outer(func):
            actor = self._actor_system.createActor(EventActor)
            self._actor_system.ask(actor, EventMessage("add_event", func, event))
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                self._actor_system.tell(actor, EventMessage("emit", event, *args, **kwargs))
                return func(*args, **kwargs)
            
            return wrapper
        
        return outer

    def remove_event(self, func_name: str, event: str) -> None:
        """Removes a subscribed function from a specific event.

        Args:
            func_name: The name of the function to be removed.
            event: The name of the event.

        """
        actor = self._actor_system.createActor(EventActor)
        self._actor_system.ask(actor, EventMessage("remove_event", func_name, event))
