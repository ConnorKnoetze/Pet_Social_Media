
class TestUserMethods:
    def test_add_pet_user(self, in_memory_repository, test_pet_user):
        original_users_len = len(in_memory_repository.get_pet_users())
        in_memory_repository.add_pet_user(test_pet_user)
        assert in_memory_repository.get_total_user_size() == original_users_len + 1

    def test_add_multiple_pet_users(
        self, in_memory_repository, test_pet_user
    ):
        original_users_len = len(in_memory_repository.get_pet_users())
        pet_user = test_pet_user
        pet_user.username = "<NAME>"
        in_memory_repository.add_multiple_pet_users([test_pet_user, pet_user])
        assert in_memory_repository.get_total_user_size() == original_users_len + 2

    def test_get_pet_users(self, in_memory_repository, test_pet_user):
        in_memory_repository.add_pet_user(test_pet_user)
        pet_users = in_memory_repository.get_pet_users()
        assert len(pet_users) > 0
        assert test_pet_user in pet_users

    def test_get_pet_user_by_name(
        self, in_memory_repository, test_pet_user
    ):
        in_memory_repository.add_pet_user(test_pet_user)
        retrieved_user = in_memory_repository.get_pet_user_by_name(
            test_pet_user.username
        )
        assert retrieved_user is not None
        assert retrieved_user.username == test_pet_user.username

    def test_get_pet_user_by_id(self, in_memory_repository, test_pet_user):
        in_memory_repository.add_pet_user(test_pet_user)
        retrieved_user = in_memory_repository.get_pet_user_by_id(
            test_pet_user.id
        )
        assert retrieved_user is not None
        assert retrieved_user.id == test_pet_user.id

    def test_get_all_user_post_paths(
        self, in_memory_repository, test_pet_user, test_post
    ):
        in_memory_repository.add_pet_user(test_pet_user)
        in_memory_repository.add_post(test_pet_user, test_post)
        post_paths = in_memory_repository.get_all_user_post_paths(
            test_pet_user
        )
        assert len(post_paths) == 1
        assert post_paths[0] == str(test_post.media_path)

