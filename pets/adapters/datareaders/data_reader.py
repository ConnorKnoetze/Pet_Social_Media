from typing import List
from pets.adapters.datareaders.comments_reader import CommentsReader
from pets.adapters.datareaders.likes_reader import LikesReader
from pets.adapters.datareaders.pet_user_reader import PetUserReader
from pets.adapters.datareaders.posts_reader import PostsReader
from pets.domainmodel.Comment import Comment
from pets.domainmodel.Like import Like
from pets.domainmodel.PetUser import PetUser
from pets.domainmodel.Post import Post


class DataReader:
    def __init__(self):
        pet_user_reader = PetUserReader()
        posts_reader = PostsReader()
        likes_reader = LikesReader()
        comments_reader = CommentsReader()

        pet_user_reader.read_pet_users()
        posts_reader.read_posts()
        likes_reader.read_likes()
        comments_reader.read_comments()

        posts_reader.assign_likes(likes_reader.likes)
        posts_reader.assign_comments(comments_reader.comments)
        pet_user_reader.assign_posts(posts_reader.posts)

        self.__pet_users = pet_user_reader.users
        self.__posts = posts_reader.posts
        self.__likes = likes_reader.likes
        self.__comments = comments_reader.comments
        self.__max_like_id = likes_reader.max_like_id

    @property
    def users(self) -> List[PetUser]:
        return self.__pet_users

    @property
    def posts(self) -> List[Post]:
        return self.__posts

    @property
    def likes(self) -> List[Like]:
        return self.__likes

    @property
    def comments(self) -> List[Comment]:
        return self.__comments

    @property
    def max_like_id(self) -> int:
        return self.__max_like_id


if __name__ == "__main__":
    data_reader = DataReader()
    for user in data_reader.users:
        print(user)
    for post in data_reader.posts:
        print(post)
    for like in data_reader.likes:
        print(like)
    for comment in data_reader.comments:
        print(comment)
