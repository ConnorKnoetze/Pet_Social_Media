from typing import List

from pets.adapters.repository import AbstractRepository, RepositoryException
from pets.domainmodel import User, PetUser, Post, Comment


class MemoryRepository(AbstractRepository):
    def __init__(self):
        self.__human_users = list()
        self.__pet_users = list()
        self.__posts = list()
        self.__comments = list()  # might not need this but it could come in userful

    def populate(self, users:List[User]) -> None:
        self.__pet_users = users
        self.__posts = [user.posts for user in users]
        self.__comments = [user.comments for user in users]
        #self.__human_users = [user.human_user for user in users]

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
        for user in self.__human_users:
            if user.username == username:
                return user
        return None

    def get_photo_posts(self) -> List[Post]:
        image_posts = []
        for user_posts in self.__posts:
            for post in user_posts:
                if post.media_type == 'photo':
                    image_posts.append(post)
        return image_posts

    def get_pet_user_by_name(self, username) -> User:
        for user in self.__pet_users:
            if user.username == username:
                return user
        return None

    #def get_user_by_id(self, id: int) -> User:


    def get_human_user_by_id(self, id: int) -> User:
        for user in self.__human_users:
            if user.id == id:
                return user
        return None

    def get_pet_user_by_id(self, id: int) -> User:
        for user in self.__pet_users:
            if user.id == id:
                return user
        return None

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
        return self.__posts.remove(post)

    def get_post_by_id(self, id: int) -> Post:
        for post in self.__posts:
            if post.id == id:
                return post
        return None

    def add_comment(self, user: User, comment: Comment):
        user.add_comment(comment)
        self.__comments.append(comment)

    def get_comments_by_post(self, post: Post) -> List[Comment]:
        comments_for_post = []
        for comment in self.__comments:
            if comment.post == post:
                comments_for_post.append(comment)
        return comments_for_post

    def add_multiple_comments(self, users: List[User], comments: List[Comment]):
        for user, comment in zip(users, comments):
            user.add_comment(comment)
            self.__comments.append(comment)


    def add_like(self, post: Post, user: User):
        post.add_like(user)


    def add_multiple_likes(self, posts: List[Post], users: List[User]):
        for post, user in zip(posts, users):
            post.add_like(user)

    def delete_comment(self, user: User, comment: Comment):
        user.comments.remove(comment)
        return self.__comments.remove(comment)
