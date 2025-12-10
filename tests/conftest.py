from pathlib import Path

import pytest

from datetime import datetime

from pets import create_app, MemoryRepository, populate
from pets.domainmodel.User import User
from pets.domainmodel.PetUser import PetUser
from pets.domainmodel.HumanUser import HumanUser
from pets.domainmodel.Post import Post

from pets.adapters.datareaders.pet_user_reader import PetUserReader
from pets.adapters.datareaders.posts_reader import PostsReader
from pets.adapters.datareaders.likes_reader import LikesReader
from pets.adapters.datareaders.comments_reader import CommentsReader


@pytest.fixture(scope="session", autouse=True)
def test_user():
    user: User = User(
        1,
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
        1,
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
        1,
        "pet_user",
        "pet_user.example.com",
        "hashed_password",
        Path(""),
        datetime.now(),
    )
    return pet_user


@pytest.fixture(scope="function", autouse=True)
def test_comment(test_user, test_post):
    from pets.domainmodel.Comment import Comment

    comment: Comment = Comment(
        1, test_user.user_id, test_post.id, datetime.now(), "This is a test comment", 0
    )
    return comment


@pytest.fixture(scope="function", autouse=True)
def test_post(test_pet_user):
    post: Post = Post(
        1,
        test_pet_user.user_id,
        "this is a test post",
        1,
        datetime.now(),
        (180, 180),
        [],
        [test_pet_user],
        Path(""),
        "photo",
    )
    return post


@pytest.fixture(scope="function", autouse=True)
def test_like(test_user, test_post):
    from pets.domainmodel.Like import Like

    like: Like = Like(
        1,
        test_user.user_id,
        test_post.id,
        datetime.now(),
    )
    return like


@pytest.fixture(scope="function", autouse=True)
def test_pet_user_reader():
    pet_user_reader = PetUserReader()
    return pet_user_reader


@pytest.fixture(scope="function", autouse=True)
def test_posts_reader():
    posts_reader = PostsReader()
    return posts_reader


@pytest.fixture(scope="function", autouse=True)
def test_likes_reader():
    likes_reader = LikesReader()
    return likes_reader


@pytest.fixture(scope="function", autouse=True)
def test_comments_reader():
    comments_reader = CommentsReader()
    return comments_reader


@pytest.fixture
def in_memory_repository() -> MemoryRepository:
    repository = MemoryRepository()
    populate(repository)
    return repository


@pytest.fixture(scope="function", autouse=True)
def client():
    my_app = create_app()

    with my_app.test_client() as client:
        yield client
