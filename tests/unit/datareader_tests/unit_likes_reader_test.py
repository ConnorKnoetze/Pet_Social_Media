from datetime import datetime

from pets.adapters.datareaders.likes_reader import LikesReader


def test_likes_reader(test_likes_reader):
    assert isinstance(test_likes_reader, LikesReader)
    likes = test_likes_reader.read_likes()
    assert isinstance(likes, list)
    assert all(hasattr(like, "id") for like in likes)
    assert all(hasattr(like, "user_id") for like in likes)
    assert all(hasattr(like, "post_id") for like in likes)
    assert all(hasattr(like, "created_at") for like in likes)


def test_likes_reader_like_attributes(test_likes_reader):
    likes = test_likes_reader.read_likes()
    for like in likes:
        assert isinstance(like.id, int)
        assert isinstance(like.user_id, int)
        assert isinstance(like.post_id, int)
        assert isinstance(like.created_at, datetime)


def test_likes_reader_multiple_likes(test_likes_reader):
    likes = test_likes_reader.read_likes()
    assert len(likes) > 1
    user_ids = [like.user_id for like in likes]
    post_ids = [like.post_id for like in likes]
    assert len(set(user_ids)) > 1
    assert len(set(post_ids)) > 1


def test_likes_reader_created_at_type(test_likes_reader):
    likes = test_likes_reader.read_likes()
    for like in likes:
        assert hasattr(like, "created_at")
        assert hasattr(like.created_at, "year")
        assert hasattr(like.created_at, "month")
        assert hasattr(like.created_at, "day")
        assert hasattr(like.created_at, "hour")
        assert hasattr(like.created_at, "minute")
        assert hasattr(like.created_at, "second")


def test_likes_reader_no_likes_initially(test_likes_reader):
    assert test_likes_reader.likes == []


def test_likes_reader_likes_property(test_likes_reader):
    likes = test_likes_reader.read_likes()
    assert test_likes_reader.likes == likes
    assert all(isinstance(like, type(likes[0])) for like in test_likes_reader.likes)


def test_likes_reader_reads_multiple_likes(test_likes_reader):
    likes = test_likes_reader.read_likes()
    assert len(likes) > 1
    user_ids = [like.user_id for like in likes]
    post_ids = [like.post_id for like in likes]
    assert len(set(user_ids)) > 1
    assert len(set(post_ids)) > 1
