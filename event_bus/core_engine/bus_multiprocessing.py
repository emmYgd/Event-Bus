from functools import wraps
from multiprocessing import Process, Manager
from collections import defaultdict
from typing import Callable, List, Dict, Any, Union

class EventBus:
    def __init__(self):
        self._events = defaultdict(set)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.event_count} subscribed events>"

    def __str__(self):
        return str(self.__class__.__name__)

    @property
    def event_count(self):
        """Returns the total number of subscribed events."""
        return sum(len(funcs) for funcs in self._events.values())

    def on(self, event: str) -> Callable:
        """Decorator for subscribing a function to a specific event.

        Args:
            event: Name of the event to subscribe to.

        Returns:
            The outer function.

        """
        def outer(func):
            self.add_event(func, event)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return outer

    def add_event(self, func: Callable, event: str) -> None:
        """Adds a function to an event.

        Args:
            func: The function to call when the event is emitted.
            event: Name of the event.

        """
        self._events[event].add(func)

    def emit(self, event: str, *args, **kwargs) -> None:
        """Emits an event and runs the subscribed functions concurrently.

        Args:
            event: Name of the event.

        """
        manager = Manager()
        event_funcs = list(self._events[event])

        processes = [
            Process(target=func, args=args, kwargs=kwargs)
            for func in event_funcs
        ]

        for process in processes:
            process.start()

        for process in processes:
            process.join()

    def emit_only(self, event: str, func_names: Union[str, List[str]], *args, **kwargs) -> None:
        """Specifically emits certain subscribed events.

        Args:
            event: Name of the event.
            func_names: Function(s) to emit.

        """
        if isinstance(func_names, str):
            func_names = [func_names]

        event_funcs = list(self._events[event])

        processes = [
            Process(target=func, args=args, kwargs=kwargs)
            for func in event_funcs
            if func.__name__ in func_names
        ]

        for process in processes:
            process.start()

        for process in processes:
            process.join()

    def emit_after(self, event: str) -> Callable:
        """Decorator that emits events after the function is completed.

        Args:
            event: Name of the event.

        Returns:
            Callable.

        """
        def outer(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                returned = func(*args, **kwargs)
                self.emit(event)
                return returned

            return wrapper

        return outer

    def remove_event(self, func_name: str, event: str) -> None:
        """Removes a subscribed function from a specific event.

        Args:
            func_name: The name of the function to be removed.
            event: The name of the event.

        """
        self._events[event] = {func for func in self._events[event] if func.__name__ != func_name}
