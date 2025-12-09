from pets.domainmodel.AnimalType import AnimalType


class TestPetUser:
    def test_pet_user_creation(self, test_pet_user):
        assert test_pet_user.username == "pet_user"
        assert test_pet_user.email == "pet_user.example.com"

    def test_add_post(self, test_pet_user, test_post):
        test_pet_user.add_post(test_post)
        assert test_post in test_pet_user.posts

    def test_delete_post(self, test_pet_user, test_post):
        test_pet_user.add_post(test_post)
        test_pet_user.delete_post(test_post)
        assert test_post not in test_pet_user.posts

    def test_add_follower(self, test_pet_user, test_user):
        test_pet_user.add_follower(test_user.user_id)
        assert test_user.user_id in test_pet_user.follower_ids

    def test_remove_follower(self, test_pet_user, test_user):
        test_pet_user.add_follower(test_user)
        test_pet_user.remove_follower(test_user)
        assert test_user not in test_pet_user.follower_ids

    def test_animal_type_property(self, test_pet_user):
        test_pet_user._PetUser__animal_type = AnimalType.CAT
        assert test_pet_user.animal_type == AnimalType.CAT

    def test_posts_initialization(self, test_pet_user):
        assert isinstance(test_pet_user.posts, list)
        assert len(test_pet_user.posts) == 0

    def test_followers_initialization(self, test_pet_user):
        assert isinstance(test_pet_user.follower_ids, list)
        assert len(test_pet_user.follower_ids) == 0

    def test_add_duplicate_post(self, test_pet_user, test_post):
        test_pet_user.add_post(test_post)
        test_pet_user.add_post(test_post)  # Attempt to add duplicate
        assert test_pet_user.posts.count(test_post) == 1

    def test_remove_nonexistent_post(self, test_pet_user, test_post):
        initial_count = len(test_pet_user.posts)
        test_pet_user.delete_post(test_post)  # Attempt to remove non-existent
        assert len(test_pet_user.posts) == initial_count

    def test_add_duplicate_follower(self, test_pet_user, test_user):
        test_pet_user.add_follower(test_user.user_id)
        test_pet_user.add_follower(test_user.user_id)  # Attempt to add duplicate
        assert test_pet_user.follower_ids.count(test_user.user_id) == 1

    def test_remove_nonexistent_follower(self, test_pet_user, test_user):
        initial_count = len(test_pet_user.follower_ids)
        test_pet_user.remove_follower(test_user)  # Attempt to remove non-existent
        assert len(test_pet_user.follower_ids) == initial_count
