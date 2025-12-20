from abc import ABC
from typing import List, Tuple
from pathlib import Path

from sqlalchemy import func, select, text, inspect
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.exc import NoResultFound


from pets.adapters.repository import AbstractRepository
from pets.domainmodel.User import User
from pets.domainmodel.PetUser import PetUser
from pets.domainmodel.HumanUser import HumanUser
from pets.domainmodel.Post import Post
from pets.domainmodel.Comment import Comment
from pets.domainmodel.Like import Like

from pets.adapters.orm import users_table
from pets.adapters.orm import posts_table
from pets.adapters.orm import comments_table
from pets.adapters.orm import like_table
from pets.adapters.orm import user_following_table

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


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
    _temp_users: List[User]

    def __init__(self, session_factory, database_uri: str):
        self._session_cm = SessionContextManager(session_factory)
        self._engine = create_engine(database_uri, future=True)
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)
        self._temp_users = []

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

    def create_post(
        self,
        user: PetUser,
        caption: str,
        tags: List[str],
        media_path: Path,
        media_type: str,
    ) -> Post:
        from datetime import datetime, UTC

        with self._session_cm as scm:
            # determine next post ID
            max_id = scm.session.scalar(select(func.max(posts_table.c.id)))
            next_id = 1 if max_id is None else int(max_id) + 1

            post = Post(
                id=next_id,
                user_id=user.user_id,
                caption=caption,
                created_at=datetime.now(UTC),
                media_path=media_path,
                media_type=media_type,
                views=0,
                size=(0, 0),
                tags=tags,
                users_tagged=[],
            )
            with scm.session.no_autoflush:
                scm.session.add(post)
            scm.commit()
            print(post)
            return post

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

    def get_max_like_id(self) -> int:
        with self._session_cm as scm:
            max_id = scm.session.scalar(select(func.max(like_table.c.id)))
            return 1 if max_id is None else int(max_id) + 1

    def create_like(self, user: User, post: Post) -> Like:
        from datetime import datetime
        max_like_id = self.get_max_like_id()
        return Like(
            id=max_like_id + 1,
            user_id=user.user_id,
            post_id=post.id,
            created_at=datetime.now(),
        )

    def add_like(self, user: User, post: Post):
        like = self.create_like(user, post)
        with self._session_cm as scm:
            with scm.session.no_autoflush:
                scm.session.add(like)
            scm.commit()

    def delete_like(self, user: User, post: Post):
        print("deleting like for post", post.id, "by user", user.user_id)
        with self._session_cm as scm:
            try:
                db_like = (
                    scm.session.query(Like)
                    .filter(
                        like_table.c.post_id == post.id,
                        like_table.c.user_id == user.user_id,
                    )
                    .one()
                )
                with scm.session.no_autoflush:
                    scm.session.delete(db_like)
                scm.commit()
            except NoResultFound:
                print(f"Like not found for post {post.id} by user {user.user_id}")
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
        user = self.get_pet_user_by_id(user_id)
        with self._session_cm as scm:
            posts = (
                scm.session.query(Post)
                .filter(
                    posts_table.c.user_id == user_id,
                )
                .all()
            )
            posts.sort(key=lambda p: p.created_at, reverse=True)
            return_posts = []
            for post in posts:
                if post.media_type == "photo":
                    return_posts.append(
                        {
                            "id": post.id,
                            "media_path": str(post.media_path),
                            "media_type": post.media_type,
                        }
                    )
                else:
                    video_post_thumbnail = self.get_video_thumbnail(post, user)
                    return_posts.append(
                        {
                            "id": post.id,
                            "media_path": str(video_post_thumbnail.media_path),
                            "media_type": video_post_thumbnail.media_type,
                        }
                    )
            return return_posts

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

    def unfollow_user(self, follower: User, followee: PetUser):
        with self._session_cm as scm:
            from sqlalchemy import delete

            # Check if currently following
            if not self.is_following(follower.user_id, followee.user_id):
                return

            # Delete from association table
            scm.session.execute(
                delete(user_following_table).where(
                    (user_following_table.c.follower_id == follower.user_id)
                    & (user_following_table.c.followee_id == followee.user_id)
                )
            )
            scm.commit()

            # Update domain models
            follower.unfollow(followee)
            followee.remove_follower(follower.user_id)

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
            return result is not None

    def update_user(self, user: User):
        with self._session_cm as scm:
            with scm.session.no_autoflush:
                scm.session.merge(user)
            scm.commit()

    def get_followers(self, user: User) -> List[User]:
        target_id = int(getattr(user, "user_id"))
        with self._session_factory() as session:
            return (
                session.query(users_table)
                .join(
                    user_following_table,
                    users_table.c.id == user_following_table.c.follower_id,
                )
                .filter(user_following_table.c.followee_id == target_id)
                .all()
            )

    def add_multiple_followers(self, follower_id_lists: Tuple[int, List[int]]):
        """(int followee_id, List[int] follower_ids)"""
        with self._session_cm as scm:
            for followee_id, follower_ids in follower_id_lists:
                for follower_id in follower_ids:
                    follower = self.get_pet_user_by_id(
                        follower_id
                    ) or self.get_human_user_by_id(follower_id)
                    followee = self.get_pet_user_by_id(followee_id)
                    if follower is None or followee is None:
                        continue
                    self.follow_user(follower, followee)
            scm.commit()

    def get_video_thumbnail(self, post: Post, user: User) -> Post:
        import os
        from pathlib import Path
        from uuid import uuid4
        from PIL import Image
        import cv2

        video_path = Path(post.media_path)
        final_path = video_path
        video_path = os.path.join("pets", video_path)

        if not os.path.exists(video_path):
            print("Path does not exist for video post", post.id)
            return post

        video_path = Path(video_path)
        thumb_name = f"{video_path.stem}_thumb_{uuid4().hex}.jpg"
        final_thumb_path = final_path.parent / "thumbnails" / thumb_name
        thumb_path = video_path.parent / "thumbnails" / thumb_name

        thumbnails_dir = thumb_path.parent
        if thumbnails_dir.exists():
            for existing_file in thumbnails_dir.iterdir():
                if video_path.stem in existing_file.name:
                    print("Thumbnail already exists at", existing_file)

                    return Post(
                        post.id,
                        user.user_id,
                        post.caption,
                        0,
                        post.created_at,
                        (0, 0),
                        post.tags,
                        [],
                        Path(*existing_file.parts[1:]),
                        "photo",
                    )

        thumb_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # open video with opencv
            cap = cv2.VideoCapture(str(video_path))

            if not cap.isOpened():
                print(f"Failed to open video file for post {post.id}")
                return post

            # seek to 1 second (fps * 1)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps))

            ret, frame = cap.read()
            cap.release()

            if not ret or frame is None:
                print(f"Failed to read frame from video for post {post.id}")
                return post

            # convert BGR to RGB and save
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)

            # downscale to fit within UHD
            max_w, max_h = 1920, 1080
            w, h = image.size
            scale = min(max_w / w, max_h / h, 1.0)
            if scale < 1.0:
                new_size = (int(w * scale), int(h * scale))
                image = image.resize(new_size, Image.LANCZOS)

            image.save(thumb_path, format="JPEG", quality=85, optimize=True)

        except Exception as e:
            print(f"Failed to generate thumbnail for video post {post.id}: {e}")
            return post

        print("Success generating thumbnail at", thumb_path)
        return Post(
            post.id,
            user.user_id,
            post.caption,
            0,
            post.created_at,
            (0, 0),
            post.tags,
            [],
            final_thumb_path,
            "photo",
        )

    def get_all_posts(self) -> List[type[Post]]:
        with self._session_cm as scm:
            posts = scm.session.query(Post).all()
            return posts

    def add_temp_user(self, user: User):
        self._temp_users.append(user)

    def get_temp_user_by_name(self, username: str) -> User | None:
        for user in self._temp_users:
            if user.username == username:
                return user
        return None

    def get_temp_user_by_id(self, user_id: int) -> User | None:
        for user in self._temp_users:
            if user.user_id == user_id:
                return user
        return None

    def get_temp_user_max_id(self) -> int:
        with self._session_cm as scm:
            max_id = scm.session.scalar(select(func.max(users_table.c.id)))
            next_id = 1 if max_id is None else int(max_id) + 1
            return next_id

    def convert_temp_user_to_permanent(self, temp_user: User, type: str):
        with self._session_cm as scm:
            if type == "Human":
                new_user = HumanUser(
                    user_id=temp_user.user_id,
                    username=temp_user.username,
                    email=temp_user.email,
                    password_hash=temp_user.password_hash,
                    profile_picture_path=temp_user.profile_picture_path,
                    bio=temp_user.bio,
                    created_at=temp_user.created_at,
                    following=[],
                )
            elif type == "Pet":
                new_user = PetUser(
                    user_id=temp_user.user_id,
                    username=temp_user.username,
                    profile_picture_path=temp_user.profile_picture_path,
                    bio=temp_user.bio,
                    posts=[],
                    following=[],
                )
            else:
                raise ValueError("Invalid user type specified.")

            with scm.session.no_autoflush:
                scm.session.add(new_user)
            scm.commit()
            # Remove from temp users list
            self._temp_users = [
                user for user in self._temp_users if user.user_id != temp_user.user_id
            ]
            return new_user

    def convert_human_to_pet(self, human_user: User) -> PetUser:
        with self._session_cm as scm:
            new_user = PetUser(
                user_id=human_user.user_id,
                username=human_user.username,
                email=human_user.email,
                password_hash=human_user.password_hash,
                profile_picture_path=human_user.profile_picture_path,
                bio=human_user.bio,
                posts=[],
                following=human_user.following,
            )
            with scm.session.no_autoflush:
                scm.session.delete(human_user)
                scm.session.flush()
                scm.session.add(new_user)
            scm.commit()
            return new_user

    def convert_pet_to_human(self, pet_user: User) -> HumanUser:
        with self._session_cm as scm:
            new_user = HumanUser(
                user_id=pet_user.user_id,
                username=pet_user.username,
                email=pet_user.email,
                password_hash=pet_user.password_hash,
                profile_picture_path=pet_user.profile_picture_path,
                bio=pet_user.bio,
                created_at=pet_user.created_at,
                following=pet_user.following,
            )
            with scm.session.no_autoflush:
                scm.session.delete(pet_user)
                scm.session.flush()
                scm.session.add(new_user)
            scm.commit()
            return new_user
