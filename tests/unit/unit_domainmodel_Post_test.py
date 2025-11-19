from pathlib import Path


def test_posts_initialization(test_pet_user, test_post):
    test_pet_user.add_post(test_post)
    assert isinstance(test_pet_user.posts, list)
    assert len(test_pet_user.posts) == 1
    assert test_post in test_pet_user.posts
    assert test_post.user.id == test_pet_user.id

def test_post_likes(test_pet_user, test_post, test_like):
    test_pet_user.add_post(test_post)
    initial_likes = len(test_post.likes)
    test_post.add_like(test_like)
    assert len(test_post.likes) == initial_likes + 1
    assert test_like in test_post.likes

def test_post_comments(test_pet_user, test_post, test_comment):
    test_pet_user.add_post(test_post)
    initial_comments = len(test_post.comments)
    test_post.comments.append(test_comment)
    assert len(test_post.comments) == initial_comments + 1
    assert test_comment in test_post.comments

def test_post_image_path(test_pet_user, test_post):
    test_pet_user.add_post(test_post)
    assert test_post.media_path == Path("")
    new_path = Path("/new/image/path.jpg")
    test_post._Post__media_path = new_path
    assert test_post.media_path == new_path

def test_post_timestamp(test_pet_user, test_post):
    test_pet_user.add_post(test_post)
    from datetime import timedelta
    original_timestamp = test_post.created_at
    new_timestamp = original_timestamp + timedelta(days=1)
    test_post._Post__created_at = new_timestamp
    assert test_post.created_at == new_timestamp

def test_post_dimensions(test_pet_user, test_post):
    test_pet_user.add_post(test_post)
    assert test_post.size == (180, 180)
    new_dimensions = (300, 300)
    test_post._Post__size = new_dimensions
    assert test_post.size == new_dimensions

def test_post_description(test_pet_user, test_post):
    test_pet_user.add_post(test_post)
    assert test_post.caption == "this is a test post"
    new_description = "Updated post description"
    test_post._Post__caption = new_description
    assert test_post.caption == new_description

def test_post_user_association(test_pet_user, test_post):
    test_pet_user.add_post(test_post)
    assert test_post.user == test_pet_user
    another_user = test_pet_user  # In real tests, create a different user
    test_post._Post__user = another_user
    assert test_post.user == another_user

def test_post_id(test_pet_user, test_post):
    test_pet_user.add_post(test_post)
    assert test_post.id == 1
    new_id = 2
    test_post._Post__id = new_id
    assert test_post.id == new_id

def test_add_duplicate_post(test_pet_user, test_post):
    test_pet_user.add_post(test_post)
    initial_post_count = len(test_pet_user.posts)
    test_pet_user.add_post(test_post)  # Attempt to add the same post again
    assert len(test_pet_user.posts) == initial_post_count  # Count should remain the same