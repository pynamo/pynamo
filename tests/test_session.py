from pynamo.session import ScopedSession, SessionMaker, Session

from pynamo import Model, Attribute, Table, PrimaryIndex
from pynamo.fields import String
from pynamo.op import GetItem


class TestClient:
    @classmethod
    def get_item(cls, **kwargs):
        return {
            "Item": {
                "PK": {"S": "123"},
                "email": {"S": "user@example.org"},
            },
        }


def test_scoped_session():
    scoped = ScopedSession(SessionMaker(lambda: TestClient()))

    session1 = scoped()

    session2 = scoped()

    assert session1 == session2


def test_scoped_session_with_scopefunc():
    i = 0

    def my_scope_func():
        nonlocal i
        i = i + 1
        return i

    def client_factory():
        return None

    scoped = ScopedSession(
        SessionMaker(lambda: TestClient()),
        scopefunc=my_scope_func,
    )

    session1 = scoped()

    session2 = scoped()

    assert session1 != session2


def test_session_get_item():
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
