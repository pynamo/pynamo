from pynamo.session import ScopedSession, SessionMaker, Session

from pynamo import Model, Attribute, Table, PrimaryIndex, GetItem, PutItem
from pynamo.fields import String


from typing import Any


def test_scoped_session():
    class TestClient:
        pass

    scoped = ScopedSession(SessionMaker(lambda: TestClient()))

    session1 = scoped()

    session2 = scoped()

    assert session1 == session2


def test_scoped_session_with_scopefunc():
    class TestClient:
        pass

    i = 0

    def my_scope_func():
        nonlocal i
        i = i + 1
        return i

    scoped = ScopedSession(
        SessionMaker(lambda: TestClient()),
        scopefunc=my_scope_func,
    )

    session1 = scoped()

    session2 = scoped()

    assert session1 != session2


def test_session_get_item():
    class TestClient:
        @classmethod
        def get_item(cls, **kwargs: Any):
            return {
                "Item": {
                    "PK": {"S": "123"},
                    "email": {"S": "user@example.org"},
                },
            }

    session = Session(client=TestClient())

    mytable = Table(
        "mytable",
        PrimaryIndex(Attribute("PK", String)),
    )

    class User(Model):
        __table__ = mytable
        id = Attribute(String, primary_key=True)

    op = GetItem(User).where(User.id == "123")

    res = session.execute(op)
    assert isinstance(res, User)


def test_session_put_item():
    class TestClient:
        @classmethod
        def put_item(cls, **kwargs: Any):
            return {
                "Item": {
                    "PK": {"S": "123"},
                    "email": {"S": "user@example.org"},
                },
            }

    session = Session(client=TestClient())

    mytable = Table(
        "mytable",
        PrimaryIndex(Attribute("PK", String)),
    )

    class User(Model):
        __table__ = mytable
        id = Attribute(String, primary_key=True)

    user = User(id="123")

    op = PutItem(user)

    res = session.execute(op)
    assert res == user
