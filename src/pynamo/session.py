import threading
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Union,
    cast,
)

from . import limits

if TYPE_CHECKING:
    from .model import Model
    from .op import (
        DeleteItem,
        GetItem,
        PutItem,
        Query,
        UpdateItem,
    )

from .op import DeleteItem, PutItem, TransactWriteItems, UpdateItem


class _ThreadLocalRegistry:
    def __init__(
        self, session_factory: Callable[[], Union["Session", "AsyncSession"]]
    ):
        self.session_factory = session_factory
        self.registry = threading.local()

    def __call__(self) -> Union["Session", "AsyncSession"]:
        try:
            return cast("Session", self.registry.value)
        except AttributeError:
            val = self.registry.value = self.session_factory()
            return val

    def active(self) -> bool:
        return hasattr(self.registry, "value")

    def clear(self) -> None:
        try:
            del self.registry.value
        except AttributeError:
            pass


class _AsyncThreadLocalRegistry:
    def __init__(
        self,
        session_factory: Callable[[], Awaitable["AsyncSession"]],
    ):
        self.session_factory = session_factory
        self.registry = threading.local()

    async def __call__(self) -> "AsyncSession":
        try:
            return cast("AsyncSession", self.registry.value)
        except AttributeError:
            val = await self.session_factory()
            self.registry.value = val
            return val

    def active(self) -> bool:
        return hasattr(self.registry, "value")

    def clear(self) -> None:
        try:
            del self.registry.value
        except AttributeError:
            pass


class _ScopedRegistry:
    def __init__(
        self,
        session_factory: Callable[[], Union["Session", "AsyncSession"]],
        scope_func: Callable[[], Any],
    ):
        self.registry: Dict[Any, Union["Session", "AsyncSession"]] = {}
        self.session_factory = session_factory
        self.scope_func = scope_func

    def __call__(self) -> Union["Session", "AsyncSession"]:
        key = self.scope_func()
        try:
            return self.registry[key]
        except KeyError:
            return self.registry.setdefault(key, self.session_factory())

    def active(self) -> bool:
        return self.scope_func() in self.registry

    def clear(self) -> None:
        try:
            del self.registry[self.scope_func()]
        except KeyError:
            pass


class _AsyncScopedRegistry:
    def __init__(
        self,
        session_factory: Callable[[], Awaitable["AsyncSession"]],
        scope_func: Callable[[], Any],
    ):
        self.registry: Dict[Any, "AsyncSession"] = {}
        self.session_factory = session_factory
        self.scope_func = scope_func

    async def __call__(self) -> "AsyncSession":
        key = await self.scope_func()
        try:
            return self.registry[key]
        except KeyError:
            val = await self.session_factory()
            return self.registry.setdefault(key, val)

    def active(self) -> bool:
        return self.scope_func() in self.registry

    def clear(self) -> None:
        try:
            del self.registry[self.scope_func()]
        except KeyError:
            pass


class SessionBase:
    def __init__(self, raise_on_item_limits: Optional[bool] = False):
        self.object_registry: Dict[Any, "Model"] = {}
        self.objects_to_add: Set["Model"] = set()
        self.objects_to_delete: Dict[Any, "Model"] = {}
        self.raise_on_item_limits = raise_on_item_limits

    def add(self, obj: "Model") -> None:
        if not obj.ref:
            raise Exception("no ref")

        if obj.ref not in self.object_registry:
            self.object_registry[obj.ref] = obj
            self.objects_to_add.add(obj)

    def delete(self, obj: "Model") -> None:
        if not obj.ref:
            raise Exception("no ref")
        self.objects_to_delete[obj] = obj

    def as_transaction(self) -> TransactWriteItems:
        items: List[Union[DeleteItem, PutItem, UpdateItem]] = []

        for obj in self.objects_to_delete:
            items.append(DeleteItem(obj))

        for obj in self.objects_to_add:
            if obj not in self.objects_to_delete:
                items.append(PutItem(obj))

        for _, obj in self.object_registry.items():
            if obj not in self.objects_to_delete and obj.modified_attributes():
                items.append(UpdateItem(obj))

        if (
            self.raise_on_item_limits
            and len(items) > limits.TRANSACT_WRITE_ITEMS
        ):
            raise Exception("limit")

        return TransactWriteItems(*items)

    def clear(self) -> None:
        self.objects_to_add.clear()
        self.objects_to_delete.clear()


class Session(SessionBase):
    def __init__(self, client: Any, **kwargs: Any):
        super().__init__(**kwargs)
        self.client = client

    def _get_item(self, op: "GetItem") -> "Model":
        if op.instance.ref in self.object_registry:
            return op.instance

        client_func = self.client.get_item

        res = client_func(**op.to_dynamodb())

        model_cls = op.model_cls

        instance = model_cls.from_dynamodb_item(res["Item"])

        self.object_registry[op.instance.ref] = instance
        return instance

    def _put_item(self, op: "PutItem") -> "Model":
        client_func = self.client.put_item

        client_func(**op.to_dynamodb())

        self.object_registry[op.instance.ref] = op.instance
        return op.instance

    def execute(self, op: Union["GetItem", "PutItem", "Query"]) -> Any:
        if op.__class__.__name__ == "GetItem":
            return self._get_item(cast("GetItem", op))

        if op.__class__.__name__ == "PutItem":
            return self._put_item(cast("PutItem", op))

        raise NotImplementedError()

    def save(self) -> Any:
        transaction = self.as_transaction()

        client = self.client
        return client.transact_write_items(transaction.to_dynamodb())


class AsyncSession(SessionBase):
    def __init__(self, client: Any, **kwargs: Any):
        super().__init__(**kwargs)
        self.client = client

    async def get_item(self, op: "GetItem") -> Optional["Model"]:
        if op.instance.ref in self.object_registry:
            return op.instance

        client_func = self.client.get_item

        res = await client_func(op.to_dynamodb())

        if "Item" not in res:
            return None

        model_cls = op.model_cls

        instance = model_cls.from_dynamodb_item(res["Item"])

        self.object_registry[op.instance.ref] = instance
        return instance

    async def execute(self, op: Union["GetItem", "PutItem", "Query"]) -> Any:
        if op.__class__.__name__ == "GetItem":
            return await self.get_item(cast("GetItem", op))
        raise NotImplementedError()

    async def save(self):
        transaction = self.as_transaction()

        client = self.client
        return await client.transact_write_items(transaction.to_dynamodb())


class SessionMaker:
    def __init__(self, client_factory: Callable[[], Any]):
        self.client_factory = client_factory

    def __call__(self) -> Session:
        return Session(client=self.client_factory())


class AsyncSessionMaker:
    def __init__(self, client: Any = None, **kwargs: Any):
        self.client = client
        self.kwargs = kwargs

    def __call__(self) -> AsyncSession:
        return AsyncSession(client=self.client)


class ScopedSession:
    def __init__(
        self,
        session_factory: SessionMaker,
        scopefunc: Optional[Callable[[], int]] = None,
    ) -> None:
        self.session_factory = session_factory

        self.registry: Union[_ThreadLocalRegistry, _ScopedRegistry]

        if scopefunc:
            self.registry = _ScopedRegistry(session_factory, scopefunc)
        else:
            self.registry = _ThreadLocalRegistry(session_factory)

    def __call__(self) -> Union[Session, AsyncSession]:
        return self.registry()

    def remove(self) -> None:
        # if self.registry.active():
        #    self.registry().close()
        self.registry.clear()


class AsyncScopedSession:
    def __init__(
        self,
        session_factory: AsyncSessionMaker,
        scopefunc: Optional[Callable[[], Any]] = None,
    ) -> None:
        self.session_factory = session_factory

        self.registry: Union[_AsyncThreadLocalRegistry, _AsyncScopedRegistry]

        if scopefunc:
            self.registry = _AsyncScopedRegistry(session_factory, scopefunc)
        else:
            self.registry = _AsyncThreadLocalRegistry(session_factory)

    async def __call__(self) -> AsyncSession:
        return await self.registry()

    def remove(self) -> None:
        # if self.registry.active():
        #    self.registry().close()
        self.registry.clear()
