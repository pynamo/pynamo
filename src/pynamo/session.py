import threading
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

if TYPE_CHECKING:
    from .model import Model
    from .op import (
        DeleteItem,
        GetItem,
        PutItem,
        Query,
        TransactWriteItems,
        UpdateItem,
    )


class _ThreadLocalRegistry:
    def __init__(self, factory_func: Callable[[], Any]):
        self.factory_func = factory_func
        self.registry = threading.local()

    def __call__(self):
        try:
            return self.registry.value
        except AttributeError:
            val = self.registry.value = self.factory_func()
            return val

    def active(self) -> bool:
        return hasattr(self.registry, "value")

    def clear(self):
        try:
            del self.registry.value
        except AttributeError:
            pass


class _ScopedRegistry:
    def __init__(
        self,
        factory_func: Callable[[], Any],
        scope_func: Callable[[], Any],
    ):
        self.registry: Dict[Any, Any] = {}
        self.factory_func = factory_func
        self.scope_func = scope_func

    def __call__(self) -> Any:
        key = self.scope_func()
        try:
            return self.registry[key]
        except KeyError:
            return self.registry.setdefault(key, self.factory_func())

    def active(self):
        return self.scope_func() in self.registry

    def clear(self):
        try:
            del self.registry[self.scope_func()]
        except KeyError:
            pass


class SessionBase:
    def __init__(self, raise_on_item_limits: Optional[bool] = False):
        self.object_registry: Dict[Any, "Model"] = {}
        self.objects_to_add: Set["Model"] = set()
        # self.objects_to_update: Dict[] = {}
        self.objects_to_delete: Dict[Any, "Model"] = {}
        self.raise_on_item_limits = raise_on_item_limits

    def add(self, obj: "Model"):
        if not obj.ref:
            raise Exception("no ref")

        if obj.ref not in self.object_registry:
            self.object_registry[obj.ref] = obj
            self.objects_to_add.add(obj)

    def delete(self, obj: "Model"):
        if not obj.ref:
            raise Exception("no ref")
        self.objects_to_delete[obj.ref] = obj
        self.objects_to_add.discard(obj)
        # self.objects_to_update.pop(obj.ref, None)

    def as_transaction(self):
        items = []

        for ref, obj in self.objects_to_delete:
            items.append(DeleteItem(obj))

        for ref, obj in self.objects_to_add:
            if obj.ref not in self.objects_to_delete:
                items.append(PutItem(obj))

        for ref, obj in self.object_registry:
            if ref not in self.objects_to_delete and obj.modified_attributes():
                items.append(UpdateItem(obj))

        if (
            self.raise_on_item_limits
            and len(items) > limits.TRANSACT_WRITE_ITEMS
        ):
            raise Exception("limit")

        return TransactWriteItems(*items)

    def clear(self):
        self.objects_to_add.clear()
        self.objects_to_delete.clear()


class Session(SessionBase):
    def __init__(self, client: Any, **kwargs: Any):
        super().__init__(**kwargs)
        self.client = client

    def get_item(self, op: "GetItem"):
        if op.instance.ref in self.object_registry:
            return op.instance

        client_func = getattr(self.client, "get_item")

        res = client_func(**op.to_dynamodb())

        model_cls = op.model_cls

        instance = model_cls.from_dynamodb_item(res["Item"])

        self.object_registry[op.instance.ref] = instance
        return instance

    def execute(self, op: Union["GetItem", "PutItem", "Query"]):
        if op.__class__.__name__ == "GetItem":
            return self.get_item(cast("GetItem", op))
        raise NotImplementedError()

    def save(self):
        transaction = self.as_transaction()

        client = self.client
        return client.transact_write_items(transaction.to_dynamodb())


class AsyncSession(SessionBase):
    def __init__(self, client: Any, **kwargs: Any):
        super().__init__(**kwargs)
        self.client = client


class SessionMaker:
    def __init__(self, client_factory: Callable[[], Any]):
        self.client_factory = client_factory

    def __call__(self) -> Session:
        return Session(client=self.client_factory())


class AsyncSessionMaker:
    def __init__(self, client: Any = None):
        self.client = client

    def __call__(self) -> AsyncSession:
        return AsyncSession(client=self.client)


class ScopedSession:
    def __init__(
        self,
        session_factory: Callable[[], SessionMaker],
        scopefunc: Optional[Callable[[], Any]] = None,
    ) -> None:
        self.session_factory = session_factory

        if scopefunc:
            self.registry = _ScopedRegistry(session_factory, scopefunc)
        else:
            self.registry = _ThreadLocalRegistry(session_factory)

    def __call__(self) -> Union[_ScopedRegistry, _ThreadLocalRegistry]:
        return self.registry()

    def remove(self):
        if self.registry.active():
            pass
            # self.registry().close()
        self.registry.clear()
