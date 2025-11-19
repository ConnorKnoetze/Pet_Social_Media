from datetime import datetime

class Like:
    __id: int
    __user_id: int
    __post_id: int
    __created_at: datetime

    def __init__(self, id: int, user_id: int, post_id: int, created_at: datetime):
        self.__id = id
        self.__user_id = user_id
        self.__post_id = post_id
        self.__created_at = created_at

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, value: int):
        self.__id = value

    @property
    def user_id(self) -> int:
        return self.__user_id

    @user_id.setter
    def user_id(self, value: int):
        self.__user_id = value

    @property
    def post_id(self) -> int:
        return self.__post_id

    @post_id.setter
    def post_id(self, value: int):
        self.__post_id = value

    @property
    def created_at(self) -> datetime:
        return self.__created_at

    @created_at.setter
    def created_at(self, value: datetime):
        self.__created_at = value
