from pets.domainmodel.Comment import Comment
from datetime import datetime


class TestCommentMethods:
    def test_add_comment(
        self, in_memory_repository, test_user, test_post, test_comment
    ):
        in_memory_repository.add_comment(test_user, test_comment)
        assert test_comment in in_memory_repository.get_comments_by_post(test_post)

    def test_add_multiple_comments(
        self, in_memory_repository, test_user, test_post, test_comment
    ):
        comment2 = Comment(
            999, test_user.user_id, test_post.id, datetime.now(), "Another test comment", 0
        )
        in_memory_repository.add_multiple_comments(
            [test_user, test_user], [test_comment, comment2]
        )
        comments = in_memory_repository.get_comments_by_post(test_post)
        assert test_comment in comments
        assert comment2 in comments

    def test_add_like_to_comment(
        self, in_memory_repository, test_user, test_post, test_comment
    ):
        in_memory_repository.add_comment(test_user, test_comment)
        original_likes_len = test_comment.likes
        in_memory_repository.add_like_to_comment(test_comment)
        assert test_comment.likes == original_likes_len + 1

    def test_delete_comment(
        self, in_memory_repository, test_user, test_post, test_comment
    ):
        in_memory_repository.add_comment(test_user, test_comment)
        original_comments = in_memory_repository.get_comments_by_post(test_post)
        in_memory_repository.delete_comment(test_user, test_comment)
        updated_comments = in_memory_repository.get_comments_by_post(test_post)
        assert len(updated_comments) == len(original_comments) - 1
        assert test_comment not in updated_comments

    def test_create_comment(self, in_memory_repository, test_user, test_post):
        comment = in_memory_repository.create_comment(
            test_user, test_post, "Creating a new comment"
        )
        assert comment is not None
        assert comment.comment_string == "Creating a new comment"
        assert comment.user_id == test_user.user_id
        assert comment.post_id == test_post.id
