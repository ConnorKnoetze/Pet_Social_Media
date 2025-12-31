from datetime import datetime

from pets.domainmodel.User import User


class TempUser(User):
    def __init__(
        self,
        user_id: int,
        username: str,
        email: str,
        password_hash: str,
        profile_picture_path: str = None,
        created_at=None,
        liked_posts=None,
        following=None,
        comments=None,
        bio: str = None,
    ):
        super().__init__(
            user_id,
            username,
            email,
            password_hash,
            profile_picture_path,
            created_at=created_at,
            liked_posts=liked_posts,
            following=following,
            comments=comments,
            bio=bio,
        )


if __name__ == "__main__":
    temp_user = TempUser(
        user_id=1,
        username="tempuser",
        email="",
        password_hash="hashed_password",
    )
    print(temp_user.user_id)
