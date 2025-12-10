from abc import ABC
from typing import List

from sqlalchemy import func, select, text, inspect
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.exc import NoResultFound


from pets.adapters.repository import AbstractRepository
from pets.domainmodel.User import User
from pets.domainmodel.PetUser import PetUser
from pets.domainmodel.Post import Post
from pets.domainmodel.Comment import Comment
from pets.domainmodel.Like import Like

from pets.adapters.orm import users_table
from pets.adapters.orm import posts_table
from pets.adapters.orm import comments_table
from pets.adapters.orm import like_table
from pets.adapters.orm import user_following_table


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self) -> object:
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory)

    def close_current_session(self):
        if self.__session is not None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository, ABC):
    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def add_multiple_pet_users(self, users: List[PetUser]):
        with self._session_cm as scm:
            with scm.session.no_autoflush:
                for user in users:
                    scm.session.add(user)
            scm.commit()

    def add_multiple_posts(self, users: List[User], posts: List[Post]):
        with self._session_cm as scm:
            with scm.session.no_autoflush:
                for post in posts:
                    scm.session.merge(post)
            scm.commit()

    def add_multiple_likes(self, likes: List[Like]):
        with self._session_cm as scm:
            with scm.session.no_autoflush:
                for like in likes:
                    scm.session.merge(like)
            scm.commit()

    def add_multiple_comments(self, users: User, comments: List[Comment]):
        with self._session_cm as scm:
            with scm.session.no_autoflush:
                for comment in comments:
                    scm.session.merge(comment)
            scm.commit()

    def add_pet_users(self, users: List[PetUser]):
        invalid_indexes = []
        for i, user in enumerate(users):
            username = getattr(user, "username", None)
            if username is None or (
                isinstance(username, str) and username.strip() == ""
            ):
                invalid_indexes.append(i)

        if invalid_indexes:
            raise ValueError(
                f"Refusing to add {len(invalid_indexes)} pet_user(s) with missing/empty username at indexes: "
                f"{', '.join(map(str, invalid_indexes))}. Fix the data source before populating."
            )

        with self._session_cm as scm:
            with scm.session.no_autoflush:
                for user in users:
                    scm.session.add(user)
            scm.commit()

    def get_pet_users(self) -> List[type[PetUser]]:
        with self._session_cm as scm:
            users = scm.session.query(PetUser).all()
            return users

    def get_pet_user_by_id(self, user_id: int) -> PetUser | None:
        with self._session_cm as scm:
            try:
                user = scm.session.query(PetUser).filter(PetUser.id == user_id).one()
                return user
            except NoResultFound:
                return None

    def get_pet_user_by_name(self, username: str) -> PetUser | None:
        from pets.adapters.orm import users_table

        with self._session_cm as scm:
            try:
                user = (
                    scm.session.query(PetUser)
                    .filter(users_table.c.username == username)
                    .one()
                )
                return user
            except NoResultFound:
                return None

    def add_post(self, user: PetUser, post: Post):
        with self._session_cm as scm:
            with scm.session.no_autoflush:
                scm.session.add(post)
            scm.commit()

    def get_photo_posts(self) -> List[Post]:
        from pets.adapters.orm import posts_table

        with self._session_cm as scm:
            posts = (
                scm.session.query(Post)
                .filter(posts_table.c.media_type == "photo")
                .all()
            )
            return posts

    def get_all_user_post_paths(self, user: PetUser) -> List[str]:
        with self._session_cm as scm:
            posts = scm.session.query(Post).filter(Post.user_id == user.user_id).all()
            return [str(post.media_path) for post in posts]

    def delete_post(self, user: PetUser, post: Post):
        with self._session_cm as scm:
            with scm.session.no_autoflush:
                scm.session.delete(post)
            scm.commit()

    def get_post_by_id(self, id: int) -> Post | None:
        with self._session_cm as scm:
            try:
                post = scm.session.query(Post).filter(posts_table.c.id == id).one()
                return post
            except NoResultFound:
                return None

    def get_total_user_size(self) -> int:
        with self._session_cm as scm:
            # pet users count (best-effort)
            try:
                pet_user_count = scm.session.query(PetUser).count()
            except Exception:
                try:
                    pet_user_count = int(
                        scm.session.scalar(
                            select(func.count()).select_from(
                                getattr(PetUser, "__table__", PetUser)
                            )
                        )
                        or 0
                    )
                except Exception:
                    pet_user_count = 0

            # human users count with table-exists check and fallbacks
            human_user_count = 0
            try:
                bind = scm.session.get_bind()
                inspector = inspect(bind)
                if inspector.has_table("users"):
                    # safe raw SQL when table exists
                    res = scm.session.execute(text("SELECT COUNT(*) FROM users"))
                    human_user_count = int(res.scalar() or 0)
                else:
                    human_user_count = 0
            except OperationalError:
                human_user_count = 0
            except Exception:
                # final fallback: try mapped table if present
                user_table = getattr(User, "__table__", None)
                if user_table is not None:
                    try:
                        human_user_count = int(
                            scm.session.scalar(
                                select(func.count()).select_from(user_table)
                            )
                            or 0
                        )
                    except Exception:
                        human_user_count = 0
                else:
                    human_user_count = 0

            return int((pet_user_count or 0) + (human_user_count or 0))

    def add_human_user(self, user: User):
        with self._session_cm as scm:
            with scm.session.no_autoflush:
                scm.session.add(user)
            scm.commit()

    def add_multiple_human_users(self, users: List[User]):
        with self._session_cm as scm:
            with scm.session.no_autoflush:
                for user in users:
                    scm.session.add(user)
            scm.commit()

    def get_human_user_by_name(self, username: str) -> User | None:
        with self._session_cm as scm:
            try:
                user = (
                    scm.session.query(User)
                    .filter(users_table.c.username == username)
                    .one()
                )
                return user
            except NoResultFound:
                return None

    def get_human_user_by_id(self, user_id: int) -> User | None:
        with self._session_cm as scm:
            try:
                user = scm.session.query(User).filter(users_table.c.id == user_id).one()
                return user
            except NoResultFound:
                return None

    def get_human_users(self) -> List[type[User]]:
        with self._session_cm as scm:
            users = scm.session.query(User).all()
            return users

    def add_pet_user(self, user: PetUser):
        with self._session_cm as scm:
            with scm.session.no_autoflush:
                scm.session.add(user)
            scm.commit()

    def add_comment(self, user: User, comment: Comment):
        with self._session_cm as scm:
            with scm.session.no_autoflush:
                scm.session.merge(comment)
            scm.commit()

    def get_comments_by_post(self, post: Post) -> List[Comment]:
        with self._session_cm as scm:
            comments = (
                scm.session.query(Comment)
                .filter(comments_table.c.post_id == post.id)
                .all()
            )
            return comments

    def get_comments_for_post(self, post_id: int) -> List[Comment]:
        with self._session_cm as scm:
            comments = (
                scm.session.query(Comment)
                .filter(comments_table.c.post_id == post_id)
                .all()
            )
            return comments

    def add_like(self, user: User, like: Like):
        print(user)
        with self._session_cm as scm:
            with scm.session.no_autoflush:
                scm.session.merge(like)
            scm.commit()

    def delete_like(self, post: Post, user: User):
        with self._session_cm as scm:
            try:
                like = (
                    scm.session.query(Like)
                    .filter(
                        like_table.c.post_id == post.id,
                        like_table.c.user_id == user.user_id,
                    )
                    .one()
                )
                with scm.session.no_autoflush:
                    scm.session.delete(like)
                scm.commit()
            except NoResultFound:
                # nothing to delete
                scm.rollback()

    def delete_comment(self, user: User, comment: Comment):
        with self._session_cm as scm:
            try:
                # attempt to find the comment by id and user to ensure ownership
                db_comment = (
                    scm.session.query(Comment)
                    .filter(
                        comments_table.c.id == comment.id,
                        comments_table.c.user_id == user.user_id,
                    )
                    .one()
                )
                with scm.session.no_autoflush:
                    scm.session.delete(db_comment)
                scm.commit()
            except NoResultFound:
                scm.rollback()

    def get_posts_thumbnails(self, user_id: int) -> List[dict]:
        with self._session_cm as scm:
            posts = (
                scm.session.query(Post)
                .filter(
                    posts_table.c.user_id == user_id,
                    posts_table.c.media_type == "photo",
                )
                .all()
            )
            return [
                {
                    "id": post.id,
                    "media_path": str(post.media_path)
                    if hasattr(post, "media_path")
                    else None,
                    "media_type": getattr(post, "media_type", None),
                }
                for post in posts
            ]

    def next_comment_id(self) -> int:
        with self._session_cm as scm:
            max_id = scm.session.scalar(select(func.max(comments_table.c.id)))
            return 1 if max_id is None else int(max_id) + 1

    def create_comment(self, user: User, post: Post, text: str) -> Comment:
        from datetime import datetime, UTC

        with self._session_cm as scm:
            cid = self.next_comment_id()
            comment = Comment(
                id=cid,
                post_id=post.id,
                user_id=user.user_id,
                created_at=datetime.now(UTC),
                comment_string=text,
                likes=0,
            )
            with scm.session.no_autoflush:
                scm.session.add(comment)
            scm.commit()
            return comment

    def add_like_to_comment(self, comment: Comment):
        with self._session_cm as scm:
            try:
                db_comment = (
                    scm.session.query(Comment)
                    .filter(comments_table.c.id == comment.id)
                    .one()
                )
                db_comment.add_like()
                with scm.session.no_autoflush:
                    scm.session.merge(db_comment)
                scm.commit()
            except NoResultFound:
                scm.rollback()

    def close_session(self):
        self._session_cm.close_current_session()

    def follow_user(self, follower: User, followee: PetUser):
        with self._session_cm as scm:
            from sqlalchemy import insert

            # Check if already following
            if self.is_following(follower.user_id, followee.user_id):
                return

            # Insert into association table
            scm.session.execute(
                insert(user_following_table).values(
                    follower_id=follower.user_id, followee_id=followee.user_id
                )
            )
            scm.commit()

            # Update domain models
            follower.follow(followee)
            followee.add_follower(follower.user_id)

    def is_following(self, follower_id: int, followee_id: int) -> bool:
        """Check if a user is following another user."""
        with self._session_cm as scm:
            from sqlalchemy import select

            result = scm.session.execute(
                select(user_following_table).where(
                    (user_following_table.c.follower_id == follower_id)
                    & (user_following_table.c.followee_id == followee_id)
                )
            ).fetchone()
            print(result)
            return result is not None
