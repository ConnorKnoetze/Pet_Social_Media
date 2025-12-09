from sqlalchemy import (
    DateTime,
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import registry, relationship, column_property
import json
from datetime import datetime
from pathlib import Path

from pets.domainmodel.User import User
from pets.domainmodel.PetUser import PetUser
from pets.domainmodel.Post import Post
from pets.domainmodel.Comment import Comment
from pets.domainmodel.Like import Like
from sqlalchemy import TypeDecorator


class TagsType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        return json.loads(value)


class DateTimeType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.isoformat()

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return datetime.fromisoformat(value)


class AnimalTypeType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        from pets.domainmodel.AnimalType import AnimalType

        if isinstance(value, AnimalType):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        from pets.domainmodel.AnimalType import AnimalType

        return AnimalType(value)


class PathType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return Path(value)


class ListType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        return json.loads(value)


class SizeType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(list(value)) if value else json.dumps([0, 0])

    def process_result_value(self, value, dialect):
        if value is None:
            return (0, 0)
        data = json.loads(value)
        return tuple(data)


mapper_registry = registry()
metadata = mapper_registry.metadata

users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(255), unique=True, nullable=False),
    Column("email", String(255), unique=True, nullable=False),
    Column("password_hash", String(255), nullable=False),
    Column("profile_picture_path", PathType(500)),
    Column("created_at", DateTimeType, nullable=False),
    Column("bio", Text),
    Column("type", String(50)),
)

pet_users_table = Table(
    "pet_users",
    metadata,
    Column("id", Integer, ForeignKey("users.id"), primary_key=True),
    # store animal_type as enum/string using AnimalTypeType
    Column("animal_type", AnimalTypeType, nullable=True),
    # store follower ids as a json list
    Column("follower_ids", ListType, nullable=True),
)

posts_table = Table(
    "posts",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("pet_users.id"), nullable=False),
    Column("caption", Text, nullable=True),
    Column("views", Integer, nullable=False, default=0),
    Column("created_at", DateTimeType, nullable=False),
    Column("size", SizeType, nullable=False),
    Column("tags", TagsType, nullable=False),
    Column("media_path", PathType, nullable=False),
    Column("media_type", String(50), nullable=False),
)

post_user_association = Table(
    "post_user_association",
    metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("pet_users.id"), primary_key=True),
)

comments_table = Table(
    "comments",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("post_id", Integer, ForeignKey("posts.id"), nullable=False),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("text", Text, nullable=False),
    Column("created_at", DateTimeType, nullable=False),
    Column("likes", Integer, nullable=False, default=0),
)

like_table = Table(
    "likes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("pet_users.id"), nullable=False),
    Column("post_id", Integer, ForeignKey("posts.id"), nullable=False),
    Column("created_at", DateTimeType, nullable=False),
)


def map_model_to_tables():
    mapper_registry.map_imperatively(
        User,
        users_table,
        polymorphic_on=users_table.c.type,
        polymorphic_identity="user",
        properties={
            "_User__user_id": users_table.c.id,
            "_User__username": users_table.c.username,
            "_User__email": users_table.c.email,
            "_User__password_hash": users_table.c.password_hash,
            "_User__profile_picture_path": users_table.c.profile_picture_path,
            "_User__created_at": users_table.c.created_at,
            "_User__bio": users_table.c.bio,
        },
    )

    mapper_registry.map_imperatively(
        PetUser,
        pet_users_table,
        inherits=User,
        polymorphic_identity="pet_user",
        properties={
            # posts relationship to Post
            "_PetUser__posts": relationship(
                Post, back_populates="_Post__user", cascade="all, delete-orphan"
            ),
            # animal_type stored as column (enum string)
            "_PetUser__animal_type": pet_users_table.c.animal_type,
            # follower ids stored as serialized list column
            "_PetUser__follower_ids": column_property(pet_users_table.c.follower_ids),
        },
    )

    mapper_registry.map_imperatively(
        Post,
        posts_table,
        properties={
            "_Post__id": posts_table.c.id,
            "_Post__user_id": posts_table.c.user_id,
            "_Post__caption": posts_table.c.caption,
            "_Post__views": posts_table.c.views,
            "_Post__created_at": posts_table.c.created_at,
            "_Post__size": posts_table.c.size,
            "_Post__tags": posts_table.c.tags,
            "_Post__media_path": posts_table.c.media_path,
            "_Post__media_type": posts_table.c.media_type,
            "_Post__user": relationship(PetUser, back_populates="_PetUser__posts"),
            "_Post__comments": relationship(
                Comment, back_populates="_Comment__post", cascade="all, delete-orphan"
            ),
            "_Post__likes": relationship(
                Like, back_populates="_Like__post", cascade="all, delete-orphan"
            ),
        },
    )

    mapper_registry.map_imperatively(
        Comment,
        comments_table,
        properties={
            "_Comment__id": comments_table.c.id,
            "_Comment__user_id": comments_table.c.user_id,
            "_Comment__post_id": comments_table.c.post_id,
            "_Comment__created_at": comments_table.c.created_at,
            "_Comment__comment_string": comments_table.c.text,
            "_Comment__likes": comments_table.c.likes,
            "_Comment__post": relationship(Post, back_populates="_Post__comments"),
        },
    )

    mapper_registry.map_imperatively(
        Like,
        like_table,
        properties={
            "_Like__id": like_table.c.id,
            "_Like__user_id": like_table.c.user_id,
            "_Like__post_id": like_table.c.post_id,
            "_Like__created_at": like_table.c.created_at,
            "_Like__post": relationship(Post, back_populates="_Post__likes"),
        },
    )
