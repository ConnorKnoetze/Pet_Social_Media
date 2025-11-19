from pathlib import Path

import pytest

from datetime import datetime
from pets.domainmodel.User import User
from pets.domainmodel.PetUser import PetUser
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


@pytest.fixture(scope="function", autouse=True)
def test_pet_user():
    pet_user: PetUser = PetUser(
        "pet_user",
        "pet_user.example.com",
        "hashed_password",
        Path(""),
        datetime.now(),
    )
    return pet_user
