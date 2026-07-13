from __future__ import annotations

from typing import Any, Callable, TypeVar

T = TypeVar("T")


class ServiceContainer:
    def __init__(self):
        self._services: dict[type, Any] = {}
        self._factories: dict[type, Callable[[], Any]] = {}
        self._singletons: dict[type, Any] = {}
        self._instances: dict[type, Any] = {}

    def register(self, interface: type[T], implementation: type[T] | Callable[[], T], singleton: bool = True) -> None:
        if singleton:
            self._services[interface] = implementation
        else:
            self._factories[interface] = implementation

    def register_instance(self, interface: type[T], instance: T) -> None:
        self._services[interface] = instance
        self._singletons[interface] = instance

    def resolve(self, interface: type[T]) -> T:
        if interface in self._singletons:
            return self._singletons[interface]

        if interface in self._services:
            service = self._services[interface]
            if callable(service) and not isinstance(service, type):
                instance = service()
            else:
                instance = service

            if interface in self._factories:
                return instance
            else:
                self._singletons[interface] = instance
                return instance

        if interface in self._factories:
            return self._factories[interface]()

        raise ValueError(f"Service not registered: {interface}")

    def is_registered(self, interface: type) -> bool:
        return interface in self._services or interface in self._factories

    def clear(self) -> None:
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._instances.clear()


class ServiceLocator:
    _instance: ServiceContainer | None = None

    @classmethod
    def get_container(cls) -> ServiceContainer:
        if cls._instance is None:
            cls._instance = ServiceContainer()
        return cls._instance

    @classmethod
    def set_container(cls, container: ServiceContainer) -> None:
        cls._instance = container

    @classmethod
    def resolve(cls, interface: type[T]) -> T:
        return cls.get_container().resolve(interface)

    @classmethod
    def register(cls, interface: type[T], implementation: type[T] | Callable[[], T], singleton: bool = True) -> None:
        cls.get_container().register(interface, implementation, singleton)

    @classmethod
    def register_instance(cls, interface: type[T], instance: T) -> None:
        cls.get_container().register_instance(interface, instance)