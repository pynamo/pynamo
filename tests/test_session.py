from pynamo.session import ScopedSession, SessionMaker


def test_scoped_session():
    scoped = ScopedSession(SessionMaker())

    session1 = scoped()

    session2 = scoped()

    assert session1 == session2


def test_scoped_session_with_scopefunc():
    i = 0

    def my_scope_func():
        nonlocal i
        i = i + 1
        return i

    scoped = ScopedSession(
        SessionMaker(),
        scopefunc=my_scope_func,
    )

    session1 = scoped()

    session2 = scoped()

    assert session1 != session2
