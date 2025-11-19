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

    def __eq__(self, other):
        if not isinstance(other, Like):
            return False
        return (
            self.id == other.id
            and self.user_id == other.user_id
            and self.post_id == other.post_id
        )

    @property
    def id(self) -> int:
        return self.__id

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def post_id(self) -> int:
        return self.__post_id

    @property
    def created_at(self) -> datetime:
        return self.__created_at
