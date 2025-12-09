from datetime import datetime
from pathlib import Path

from pets.domainmodel.Post import Post


def test_pet_user_reader(test_pet_user_reader):
    pet_users = test_pet_user_reader.read_pet_users()
    assert isinstance(pet_users, list)
    assert all(hasattr(user, "username") for user in pet_users)
    assert all(hasattr(user, "email") for user in pet_users)


def test_assign_posts_to_pet_users(test_pet_user_reader, test_post):
    pet_users = test_pet_user_reader.read_pet_users()
    test_pet_user_reader.assign_posts([test_post])
    user_with_post = next(
        (user for user in pet_users if user.user_id == test_post.user_id), None
    )
    if user_with_post:
        assert test_post in user_with_post.posts


def test_pet_user_reader_users_property(test_pet_user_reader):
    pet_users = test_pet_user_reader.read_pet_users()
    assert test_pet_user_reader.users == pet_users
    assert all(
        isinstance(user, type(pet_users[0])) for user in test_pet_user_reader.users
    )


def test_pet_user_reader_no_users_initially(test_pet_user_reader):
    assert test_pet_user_reader.users == []


def test_pet_user_reader_reads_multiple_users(test_pet_user_reader):
    pet_users = test_pet_user_reader.read_pet_users()
    assert len(pet_users) > 1
    usernames = [user.username for user in pet_users]
    assert "tulip80" in usernames
    assert "honey69" in usernames


def test_pet_user_reader_user_attributes(test_pet_user_reader):
    pet_users = test_pet_user_reader.read_pet_users()
    for user in pet_users:
        assert isinstance(user.user_id, int)
        assert isinstance(user.username, str)
        assert isinstance(user.email, str)
        assert isinstance(user.password_hash, str)
        assert hasattr(user, "profile_picture_path")
        assert hasattr(user, "created_at")
        assert hasattr(user, "bio")


def test_pet_user_reader_assigns_posts_correctly(test_pet_user_reader, test_post):
    pet_users = test_pet_user_reader.read_pet_users()
    test_pet_user_reader.assign_posts([test_post])
    for user in pet_users:
        if user.user_id == test_post.user_id:
            assert test_post in user.posts
        else:
            assert test_post not in user.posts


def test_pet_user_reader_handles_no_posts(test_pet_user_reader):
    pet_users = test_pet_user_reader.read_pet_users()
    test_pet_user_reader.assign_posts([])
    for user in pet_users:
        assert user.posts == []


def test_pet_user_reader_multiple_posts_assignment(
    test_pet_user_reader, test_post, test_pet_user
):
    pet_users = test_pet_user_reader.read_pet_users()
    another_post = Post(
        1,
        test_pet_user.user_id,
        "this is a test post",
        1,
        datetime.now(),
        (180, 180),
        [],
        [test_pet_user],
        Path(""),
        "image",
    )
    test_pet_user_reader.assign_posts([test_post, another_post])
    user_with_posts = next(
        (user for user in pet_users if user.user_id == test_post.user_id), None
    )
    if user_with_posts:
        assert test_post in user_with_posts.posts
        assert another_post in user_with_posts.posts
