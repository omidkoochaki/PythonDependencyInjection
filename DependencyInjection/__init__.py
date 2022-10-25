import inspect
from functools import wraps
from typing import Generic, Any, Union, Callable, Awaitable, cast, Type, Hashable, TypeVar, Dict

import logging

logger = logging.getLogger('DI')

Injectable = Union[object, Any]
Binding = Union[Type[Injectable], Hashable]
Constructor = Callable[[], Injectable]

T = TypeVar('T', bound=Injectable)

_INJECTOR = None  # Shared injector instance.


class InjectorException(Exception):
    pass


class Binder(object):
    _bindings: Dict[Binding, Constructor]

    def __init__(self) -> None:
        if _INJECTOR is None:
            raise InjectorException('initiate the injector - use initialize() function')
        self._bindings = _INJECTOR.bindings
        super().__init__()

    def bind(self, cls: Binding, instance: T) -> 'Binder':

        b = instance
        self._bindings[cls] = b
        logger.debug('Bound %s to an instance %s', cls, instance)
        return self

    @property
    def bindings(self):
        return self._bindings


class Injector(object):
    _bindings: Dict[Binding, Constructor]

    def __init__(self) -> None:
        self._bindings = {}
        super().__init__()

    def get_instance(self, cls: Binding) -> Injectable:
        """Return an instance for a class."""
        binding = self._bindings.get(cls)
        if binding:
            return binding

    @property
    def bindings(self):
        return self._bindings


def initialize():
    global _INJECTOR
    _INJECTOR = Injector()


class _ParametersInjection(Generic[T]):
    __slots__ = ('_params',)

    def __init__(self, **kwargs: Any) -> None:
        self._params = kwargs

    def __call__(self, func: Callable[..., Union[Awaitable[T], T]]) -> Callable[..., Union[Awaitable[T], T]]:

        arg_names = inspect.getfullargspec(func).args
        params_to_provide = self._params

        @wraps(func)
        def injection_wrapper(*args: Any, **kwargs: Any) -> T:
            provided_params = frozenset(
                arg_names[:len(args)]) | frozenset(kwargs.keys())
            for param, cls in params_to_provide.items():
                if param not in provided_params:
                    kwargs[param] = instance(cls)
            sync_func = cast(Callable[..., T], func)
            try:
                return sync_func(*args, **kwargs)
            except TypeError as te:
                raise te

        return injection_wrapper


class _AttributeInjection(object):
    def __init__(self, cls: Binding) -> None:
        self._cls = cls

    def __get__(self, obj: Any, owner: Any) -> Injectable:
        return instance(self._cls)


def params(**args_to_classes: Binding) -> Callable:
    """a decorator to inject args into a function.

    For example::

        @inject.params(cache=RedisCache, db=DbInterface)
        def sign_up(name, email, cache, db):
            pass
    """
    return _ParametersInjection(**args_to_classes)


def get_injector_or_die() -> Injector:
    """Return the current injector or raise an InjectorException."""
    injector = _INJECTOR
    if not injector:
        raise InjectorException('No injector is initialized - use initialize()')

    return injector


def instance(cls: Binding) -> Injectable:
    """returns an instance of a class."""
    return get_injector_or_die().get_instance(cls)


def bind(cls: Binding, instance: T):
    """Binds classes and instances"""
    b = Binder()
    return b.bind(cls, instance)


def clear() -> None:
    """Clear an existing injector if present."""
    global _INJECTOR

    if _INJECTOR is None:
        return

    _INJECTOR = None
    logger.debug('Injector Cleared')


def inject(cls: Binding) -> Injectable:
    """injects an instance of a class"""
    return _AttributeInjection(cls)
