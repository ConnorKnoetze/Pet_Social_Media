from datetime import datetime

from pets.domainmodel.Comment import Comment


class TestComment:
    def test_create_comment(self, test_comment, test_user):
        assert test_comment.id == 1
        assert test_comment.user_id == test_user.user_id
        assert test_comment.comment_string == "This is a test comment"
        assert isinstance(datetime.now(), type(test_comment.created_at))
        assert isinstance(test_comment.likes, int)

    def test_comment_str(self, test_comment):
        assert str(test_comment) == "This is a test comment"

    def test_comment_equality(self, test_comment, test_user, test_post):
        comment1 = Comment(
            1,
            user_id=test_user.user_id,
            post_id=test_post.id,
            created_at=datetime.now(),
            comment_string="This is a test comment",
            likes=0,
        )
        comment2 = Comment(
            1,
            user_id=test_user.user_id,
            post_id=test_post.id,
            created_at=datetime.now(),
            comment_string="This is a test comment",
            likes=0,
        )
        comment3 = Comment(
            2,
            user_id=test_user.user_id,
            post_id=test_post.id,
            created_at=datetime.now(),
            comment_string="Different comment",
            likes=0,
        )
        assert comment1 == comment2
        assert comment1 != comment3

    def test_comment_inequality_different_type(self, test_comment):
        assert test_comment != "not a comment object"

    def test_comment_inequality_different_id(self, test_comment, test_user, test_post):
        different_comment = Comment(
            2,
            user_id=test_comment.user_id,
            post_id=test_post.id,
            created_at=test_comment.created_at,
            comment_string=test_comment.comment_string,
            likes=test_comment.likes,
        )
        assert test_comment != different_comment

    def test_comment_inequality_different_user_id(
        self, test_comment, test_user, test_post
    ):
        different_comment = Comment(
            test_comment.user_id,
            user_id=test_comment.user_id + 1,
            post_id=test_post.id,
            created_at=test_comment.created_at,
            comment_string=test_comment.comment_string,
            likes=test_comment.likes,
        )
        assert test_comment != different_comment

    def test_comment_inequality_different_comment_string(
        self, test_comment, test_user, test_post
    ):
        different_comment = Comment(
            test_comment.user_id,
            user_id=test_comment.user_id,
            post_id=test_post.id,
            created_at=test_comment.created_at,
            comment_string="A different comment string",
            likes=test_comment.likes,
        )
        assert test_comment != different_comment

    def test_comment_string_setter(self, test_comment):
        new_comment_string = "Updated comment string"
        test_comment.comment_string = new_comment_string
        assert test_comment.comment_string == new_comment_string
