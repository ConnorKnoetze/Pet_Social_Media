from pathlib import Path

import pytest

from datetime import datetime
from pets.domainmodel.User import User
from pets.domainmodel.HumanUser import HumanUser


@pytest.fixture(scope="session", autouse=True)
def test_user():
    user: User = User(
        "test_user",
        "test_user@example.com",
        "hashed_password",
        Path(""),
        datetime.now(),
    )
    return user


@pytest.fixture(scope="session", autouse=True)
def test_human_user():
    human_user: HumanUser = HumanUser(
        "human_user",
        "human_user.example.com",
        "hashed_password",
        Path(""),
        datetime.now(),
    )
    return human_user
