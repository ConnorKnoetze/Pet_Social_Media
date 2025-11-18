import pytest

from datetime import datetime
from pets.domainmodel.User import User


@pytest.fixture(scope="session", autouse=True)
def test_user():
    user: User = User(
        "test_user", "test_user@example.com", "hashed_password", None, datetime.now()
    )
    return user
