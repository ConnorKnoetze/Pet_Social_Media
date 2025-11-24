from typing import List
from pets.adapters.repository import AbstractRepository
from pets.domainmodel.User import User
from pets.domainmodel.PetUser import PetUser
from pets.domainmodel.Post import Post
from pets.domainmodel.Comment import Comment
from pets.domainmodel.Like import Like
from datetime import datetime, UTC


class MemoryRepository(AbstractRepository):
    def __init__(self):
        self.__human_users: List[User] = []
        self.__pet_users: List[User] = []
        self.__posts: List[Post] = []
        self.__comments: List[Comment] = []
        self.__max_like_id = 0

    def populate(self, users: List[User], max_like_id) -> None:
        self.__pet_users = users
        # Flatten posts and comments
        self.__posts = [p for u in users for p in getattr(u, "posts", [])]
        self.__comments = [c for u in users for c in getattr(u, "comments", [])]
        self.__max_like_id = max_like_id

    def add_pet_user(self, user: User):
        self.__pet_users.append(user)

    def get_total_user_size(self):
        return len(self.__pet_users) + len(self.__human_users)

    def add_multiple_pet_users(self, users: List[User]):
        self.__pet_users.extend(users)

    def add_human_user(self, user: User):
        self.__human_users.append(user)

    def add_multiple_human_users(self, users: List[User]):
        self.__human_users.extend(users)

    def get_human_user_by_name(self, username) -> User:
        return next((u for u in self.__human_users if u.username == username), None)

    def get_photo_posts(self) -> List[Post]:
        return [p for p in self.__posts if getattr(p, "media_type", None) == "photo"]

    def get_pet_user_by_name(self, username) -> User:
        return next((u for u in self.__pet_users if u.username == username), None)

    # def get_user_by_id(self, id: int) -> User:

    def get_human_user_by_id(self, id: int) -> User:
        return next((u for u in self.__human_users if u.id == id), None)

    def get_pet_user_by_id(self, id: int) -> User:
        return next((u for u in self.__pet_users if u.id == id), None)

    def get_all_user_post_paths(self, user: User) -> List[str]:
        return [str(p.media_path) for p in self.__posts if p.user_id == user.id]

    def get_pet_users(self) -> List[User]:
        return self.__pet_users

    def get_human_users(self) -> List[User]:
        return self.__human_users

    def add_post(self, pet_user: PetUser, post: Post):
        self.__posts.append(post)
        pet_user.add_post(post)

    def add_multiple_posts(self, pet_user: PetUser, posts: List[Post]):
        self.__posts.extend(posts)
        for post in posts:
            pet_user.add_post(post)

    def delete_post(self, pet_user: PetUser, post: Post):
        pet_user.delete_post(post)
        self.__posts.remove(post)

    def get_post_by_id(self, id: int) -> Post:
        return next((p for p in self.__posts if p.id == id), None)

    def add_comment(self, user: User, comment: Comment):
        user.add_comment(comment)
        # Attach to post if exists
        post = self.get_post_by_id(getattr(comment, "post_id", -1))
        if post is not None:
            post.add_comment(comment)
        self.__comments.append(comment)

    # New method used by the /api/comments/<post_id> endpoint
    def get_comments_for_post(self, post_id: int) -> List[Comment]:
        post = self.get_post_by_id(post_id)
        return list(getattr(post, "comments", []) if post else [])

    # Optional: keep for internal usage if needed (fixed attribute)
    def get_comments_by_post(self, post: Post) -> List[Comment]:
        return [c for c in self.__comments if c.post_id == post.id]

    def add_multiple_comments(self, users: List[User], comments: List[Comment]):
        for user, comment in zip(users, comments):
            user.add_comment(comment)
            self.__comments.append(comment)

    def add_like(self, post: Post, user: User):
        self.__max_like_id += 1
        like = Like(self.__max_like_id, user.id, post.id, datetime.now(UTC))
        post.add_like(like)

    def add_multiple_likes(self, posts: List[Post], users: List[User]):
        for post, user in zip(posts, users):
            self.__max_like_id += 1
            like = Like(self.__max_like_id, user.id, post.id, datetime.now(UTC))
            post.add_like(like)

    def delete_comment(self, user: User, comment: Comment):
        user.comments.remove(comment)
        self.__comments.remove(comment)

    def get_posts_thumbnails(self, user_id: int) -> List[dict]:
        # Return up to 24 latest posts (photo or video) for thumbnail grid.
        items = [p for p in self.__posts if getattr(p, "user_id", None) == user_id]
        # Sort newest first if created_at exists.
        items.sort(key=lambda p: getattr(p, "created_at", None), reverse=True)
        out = []
        for p in items[:24]:
            if p.media_type == "photo":  # For now, just return photos.
                out.append(
                    {
                        "id": int(getattr(p, "id", 0)),
                        "media_type": getattr(p, "media_type", ""),
                        "media_path": str(getattr(p, "media_path", "")),
                    }
                )
        return out

    def next_comment_id(self) -> int:
        if not self.__comments:
            return 1
        return max(getattr(c, "id", 0) for c in self.__comments) + 1

    def create_comment(self, user: User, post: Post, text: str) -> Comment:
        cid = self.next_comment_id()
        comment = Comment(
            id=cid,
            user_id=getattr(user, "id", 0),
            post_id=getattr(post, "id", 0),
            created_at=datetime.now(UTC),
            comment_string=text,
            likes=0,
        )
        self.add_comment(user, comment)
        return comment
