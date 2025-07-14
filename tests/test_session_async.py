from typing import Any

from pynamo import Attribute, GetItem, Model, PrimaryIndex, PutItem, Table
from pynamo.fields import String

from pynamo.session import ScopedSession, AsyncSession, AsyncSessionMaker
import pytest


# @pytest.mark.asyncio
def test_async_scoped_session():
    class TestClient:
        pass

    scoped = ScopedSession(AsyncSessionMaker(client=TestClient()))

    session1 = scoped()

    session2 = scoped()

    assert session1 == session2
