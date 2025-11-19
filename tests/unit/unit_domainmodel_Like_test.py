from datetime import datetime

from pets.domainmodel.Like import Like


def test_like_creation(test_like, test_user, test_post):
    assert test_like.id == 1
    assert test_like.user_id == test_user.id
    assert test_like.post_id == test_post.id


def test_like_equality(test_like):
    like1 = Like(1, user_id=1, post_id=10, created_at=datetime.now())
    like2 = Like(1, user_id=1, post_id=10, created_at=datetime.now())
    like3 = Like(3, user_id=2, post_id=10, created_at=datetime.now())
    assert like1 == like2
    assert like1 != like3


def test_like_inequality_different_type(test_like):
    assert test_like != "not a like object"


def test_like_inequality_different_id(test_like):
    different_like = Like(
        2,
        user_id=test_like.user_id,
        post_id=test_like.post_id,
        created_at=test_like.created_at,
    )
    assert test_like != different_like


def test_like_inequality_different_user_id(test_like):
    different_like = Like(
        test_like.id,
        user_id=test_like.user_id + 1,
        post_id=test_like.post_id,
        created_at=test_like.created_at,
    )
    assert test_like != different_like


def test_like_inequality_different_post_id(test_like):
    different_like = Like(
        test_like.id,
        user_id=test_like.user_id,
        post_id=test_like.post_id + 1,
        created_at=test_like.created_at,
    )
    assert test_like != different_like


def test_like_created_at_is_datetime(test_like):
    assert isinstance(test_like.created_at, datetime)
