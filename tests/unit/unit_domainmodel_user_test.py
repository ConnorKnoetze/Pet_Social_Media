from pathlib import Path
from datetime import datetime


class TestUser:
    def test_user_creation(self, test_user):
        assert test_user.username == "test_user"
        assert test_user.email == "test_user@example.com"

    def test_username_setter(self, test_user):
        test_user.username = "new_username"
        assert test_user.username == "new_username"

    def test_email_setter(self, test_user):
        test_user.email = "new_email.@example.com"
        assert test_user.email == "new_email.@example.com"

    def test_add_following(self, test_user):
        from pets.domainmodel.User import User

        user_to_follow = User(
            "followed_user",
            "followed_user.example.com",
            "hashed_password",
            Path(""),
            datetime.now(),
        )
        test_user.follow(user_to_follow)
        assert user_to_follow in test_user.following

    def test_profile_picture_path_setter(self, test_user):
        new_path = Path("/new/profile/pic.png")
        test_user.profile_picture_path = new_path
        assert test_user.profile_picture_path == new_path

    def test_profile_picture_path(self, test_user):
        assert isinstance(test_user.profile_picture_path, Path)
