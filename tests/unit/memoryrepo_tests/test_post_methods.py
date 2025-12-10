class TestPostMethods:
    def test_add_post(self, in_memory_repository, test_pet_user, test_post):
        in_memory_repository.add_pet_user(test_pet_user)
        original_posts_len = len(
            in_memory_repository.get_all_user_post_paths(test_pet_user)
        )
        in_memory_repository.add_post(test_pet_user, test_post)
        assert (
            len(in_memory_repository.get_all_user_post_paths(test_pet_user))
            == original_posts_len + 1
        )

    def test_add_multiple_posts(self, in_memory_repository, test_pet_user, test_post):
        in_memory_repository.add_pet_user(test_pet_user)
        original_posts_len = len(
            in_memory_repository.get_all_user_post_paths(test_pet_user)
        )
        post2 = test_post
        post2.title = "<TITLE>"
        in_memory_repository.add_multiple_posts(test_pet_user, [test_post, post2])
        assert (
            len(in_memory_repository.get_all_user_post_paths(test_pet_user))
            == original_posts_len + 2
        )

    def test_delete_post(self, in_memory_repository, test_pet_user, test_post):
        in_memory_repository.add_pet_user(test_pet_user)
        in_memory_repository.add_post(test_pet_user, test_post)
        original_posts_len = len(
            in_memory_repository.get_all_user_post_paths(test_pet_user)
        )
        in_memory_repository.delete_post(test_pet_user, test_post)
        assert (
            len(in_memory_repository.get_all_user_post_paths(test_pet_user))
            == original_posts_len - 1
        )

    def test_get_post_by_id(self, in_memory_repository, test_pet_user, test_post):
        in_memory_repository.add_pet_user(test_pet_user)
        in_memory_repository.add_post(test_pet_user, test_post)
        retrieved_post = in_memory_repository.get_post_by_id(test_post.id)
        assert retrieved_post is not None
        assert retrieved_post.id == test_post.id
