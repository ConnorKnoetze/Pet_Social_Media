
from typing import List

from pets.adapters.repository import AbstractRepository, RepositoryException
from pets.adapters.datareaders import CommentsReader, PetUserReader, PostsReader, LikesReader
from pets.domainmodel import Pet, Comment, Post, User, HumanUser, PetUser

from pets.adapters.populate_repository import populate



class MemoryRepository(AbstractRepository):
    def __init__(self):
        self.__human_users = list()
        self.__animal_users = list()
        self.__posts = list()
        self.__comments = list() #might not need this but it could come in userful

    def add_animal_user(self, user: User):
        self.__animal_users.append(user)

    def add_human_user(self, user: User):
        self.__human_users.append(user)

    def get_human_user_by_name(self, username) -> User:
       for user in self.__human_users:
           if user.username == username:
               return user
       return None

    def get_animal_user_by_name(self, username) -> User:
        for user in self.__animal_users:
            if user.username == username:
                return user
        return None



    def get_human_user_by_id(self, id: int) -> User:
        for user in self.__human_users:
            if user.id == id:
                return user
        return None


    def get_animal_user_by_id(self, id: int) -> User:
        for user in self.__animals_users:
            if user.id == id:
                return user
        return None



    def get_animal_users(self) -> List[User]:
        return self.__animal_users

    def get_human_users(self) -> List[User]:
        return self.__human_users

    def add_post(self, post: Post):
        self.__posts.append(post)


    def delete_post(self, post: Post):
        return self.__posts.remove(post)

    def get_post_by_id(self, id: int) -> Post:
        for post in self.__posts:
            if post.id == id:
                return post
        return None

    def add_comment(self, user: User, comment: Comment):
        user.__comm

    def delete_comment(self, user: User, comment: Comment):
        raise NotImplementedError






