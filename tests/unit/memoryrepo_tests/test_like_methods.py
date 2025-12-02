class TestLikeMethods:
    def test_add_like(self, in_memory_repository, test_pet_user, test_user, test_post, test_like):
        in_memory_repository.add_pet_user(test_pet_user)
        in_memory_repository.add_post(test_pet_user, test_post)
        in_memory_repository.add_like(test_post, test_user)
        assert len(test_post.likes) == 1

    def test_delete_like(self, in_memory_repository, test_pet_user, test_user, test_post, test_like):
        in_memory_repository.add_pet_user(test_pet_user)
        in_memory_repository.add_post(test_pet_user, test_post)
        in_memory_repository.add_like(test_post, test_user)
        original_likes_len = len(test_post.likes)
        in_memory_repository.delete_like(test_post, test_user)
        assert len(test_post.likes) == original_likes_len - 1

    def test_add_multiple_likes(self, in_memory_repository, test_pet_user, test_user, test_post):
        in_memory_repository.add_pet_user(test_pet_user)
        in_memory_repository.add_post(test_pet_user, test_post)
        original_likes_len = len(test_post.likes)
        in_memory_repository.add_multiple_likes([test_post, test_post], [test_user, test_pet_user])
        assert len(test_post.likes) == original_likes_len + 2