from pathlib import Path


def test_posts_reader(test_posts_reader):
    posts = test_posts_reader.read_posts()
    assert isinstance(posts, list)
    assert all(hasattr(post, "id") for post in posts)
    assert all(hasattr(post, "user_id") for post in posts)
    assert all(hasattr(post, "caption") for post in posts)
    assert all(hasattr(post, "created_at") for post in posts)
    assert all(hasattr(post, "size") for post in posts)
    assert all(hasattr(post, "likes") for post in posts)
    assert all(hasattr(post, "comments") for post in posts)
    assert all(hasattr(post, "media_path") for post in posts)
    assert all(hasattr(post, "media_type") for post in posts)


def test_posts_reader_post_attributes(test_posts_reader):
    posts = test_posts_reader.read_posts()
    for post in posts:
        assert isinstance(post.id, int)
        assert isinstance(post.user_id, int)
        assert isinstance(post.caption, str)
        assert hasattr(post, "created_at")
        assert isinstance(post.size, tuple)
        assert isinstance(post.likes, list)
        assert isinstance(post.comments, list)
        assert isinstance(post.media_path, Path)
        assert isinstance(post.media_type, str)


def test_posts_reader_multiple_posts(test_posts_reader):
    posts = test_posts_reader.read_posts()
    assert len(posts) > 1
    captions = [post.caption for post in posts]
    assert "Tulip on Pexels" in captions
    assert "Bo on Pexels" in captions


def test_posts_reader_size_parsing(test_posts_reader):
    posts = test_posts_reader.read_posts()
    for post in posts:
        assert isinstance(post.size, tuple)
        assert len(post.size) == 2
        assert all(isinstance(dim, int) for dim in post.size)


def test_posts_reader_media_path_type(test_posts_reader):
    posts = test_posts_reader.read_posts()
    for post in posts:
        assert isinstance(post.media_path, Path)


def test_posts_reader_media_type_values(test_posts_reader):
    posts = test_posts_reader.read_posts()
    valid_media_types = {"photo", "video"}
    for post in posts:
        assert post.media_type in valid_media_types


def test_posts_reader_no_posts_initially(test_posts_reader):
    assert test_posts_reader.read_posts() != []


def test_posts_reader_reads_all_posts(test_posts_reader):
    posts = test_posts_reader.read_posts()
    assert len(posts) == 89  # There are 89 posts in the CSV file

def test_posts_reader_assign_likes_and_comments(test_posts_reader, test_likes_reader, test_comments_reader):
    posts = test_posts_reader.read_posts()
    likes = test_likes_reader.read_likes()
    comments = test_comments_reader.read_comments()

    test_posts_reader.assign_likes(likes)
    test_posts_reader.assign_comments(comments)

    for post in posts:
        post_likes = [like for like in likes if like.post_id == post.id]
        post_comments = [comment for comment in comments if comment.post_id == post.id]

        assert len(post.likes) == len(post_likes)
        assert len(post.comments) == len(post_comments)