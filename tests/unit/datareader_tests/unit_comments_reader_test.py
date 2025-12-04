from datetime import datetime


def test_comments_reader(test_comments_reader):
    comments = test_comments_reader.read_comments()
    assert isinstance(comments, list)
    assert all(hasattr(comment, "id") for comment in comments)
    assert all(hasattr(comment, "user_id") for comment in comments)
    assert all(hasattr(comment, "post_id") for comment in comments)
    assert all(hasattr(comment, "created_at") for comment in comments)
    assert all(hasattr(comment, "comment_string") for comment in comments)
    assert all(hasattr(comment, "likes") for comment in comments)


def test_comments_reader_comment_attributes(test_comments_reader):
    comments = test_comments_reader.read_comments()
    for comment in comments:
        assert isinstance(comment.id, int)
        assert isinstance(comment.user_id, int)
        assert isinstance(comment.post_id, int)
        assert isinstance(comment.created_at, datetime)
        assert isinstance(comment.comment_string, str)
        assert isinstance(comment.likes, int)


def test_comments_reader_multiple_comments(test_comments_reader):
    comments = test_comments_reader.read_comments()
    assert len(comments) > 1
    comment_strings = [comment.comment_string for comment in comments]
    assert "So cute!" in comment_strings
    assert "Nice!" in comment_strings


def test_comments_reader_no_comments_initially(test_comments_reader):
    assert test_comments_reader.comments == []


def test_comments_reader_comments_property(test_comments_reader):
    comments = test_comments_reader.read_comments()
    assert test_comments_reader.comments == comments
    assert all(
        isinstance(comment, type(comments[0]))
        for comment in test_comments_reader.comments
    )


def test_comments_reader_created_at_type(test_comments_reader):
    comments = test_comments_reader.read_comments()
    for comment in comments:
        assert hasattr(comment.created_at, "year")
        assert hasattr(comment.created_at, "month")
        assert hasattr(comment.created_at, "day")
        assert hasattr(comment.created_at, "hour")
        assert hasattr(comment.created_at, "minute")
        assert hasattr(comment.created_at, "second")


def test_comments_reader_likes_count(test_comments_reader):
    comments = test_comments_reader.read_comments()
    for comment in comments:
        assert comment.likes >= 0
