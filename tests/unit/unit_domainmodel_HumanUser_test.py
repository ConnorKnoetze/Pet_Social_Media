from pets.domainmodel.HumanUser import HumanUser


def test_human_user_creation(test_human_user: HumanUser):
    assert test_human_user.username == "human_user"
    assert test_human_user.email == "human_user.example.com"


def test_favourite_animals_initialization(test_human_user: HumanUser):
    assert isinstance(test_human_user.favourite_animals, list)
    assert len(test_human_user.favourite_animals) == 0


def test_friends_initialization(test_human_user: HumanUser):
    assert isinstance(test_human_user.friends, list)
    assert len(test_human_user.friends) == 0


def test_add_favourite_animal(test_human_user: HumanUser):
    from pets.domainmodel.AnimalType import AnimalType

    dog = AnimalType("Dog")
    test_human_user.add_favourite_animal(dog)
    assert dog in test_human_user.favourite_animals


def test_remove_favourite_animal(test_human_user: HumanUser):
    from pets.domainmodel.AnimalType import AnimalType

    cat = AnimalType("Cat")
    test_human_user.add_favourite_animal(cat)
    test_human_user.remove_favourite_animal(cat)
    assert cat not in test_human_user.favourite_animals


def test_add_duplicate_favourite_animal(test_human_user: HumanUser):
    from pets.domainmodel.AnimalType import AnimalType

    bird = AnimalType("Bird")
    test_human_user.add_favourite_animal(bird)
    test_human_user.add_favourite_animal(bird)  # Attempt to add duplicate
    assert test_human_user.favourite_animals.count(bird) == 1


def test_remove_nonexistent_favourite_animal(test_human_user: HumanUser):
    from pets.domainmodel.AnimalType import AnimalType

    fish = AnimalType("Fish")
    initial_count = len(test_human_user.favourite_animals)
    test_human_user.remove_favourite_animal(fish)  # Attempt to remove non-existent
    assert len(test_human_user.favourite_animals) == initial_count


def test_friends_property(test_human_user: HumanUser):
    from pets.domainmodel.User import User
    from pathlib import Path
    from datetime import datetime

    friend = User(
        "friend_user",
        "friend_user.example.com",
        "hashed_password",
        Path(""),
        datetime.now(),
    )
    test_human_user.friends.append(friend)
    assert friend in test_human_user.friends


def test_add_friend(test_human_user: HumanUser):
    from pets.domainmodel.User import User
    from pathlib import Path
    from datetime import datetime

    friend = User(
        "new_friend",
        "new_friend.example.com",
        "hashed_password",
        Path(""),
        datetime.now(),
    )
    test_human_user.add_friend(friend)
    assert friend in test_human_user.friends


def test_add_existing_friend(test_human_user: HumanUser):
    from pets.domainmodel.User import User
    from pathlib import Path
    from datetime import datetime

    friend = User(
        "existing_friend",
        "existing_friend.example.com",
        "hashed_password",
        Path(""),
        datetime.now(),
    )
    test_human_user.add_friend(friend)
    initial_count = len(test_human_user.friends)
    test_human_user.add_friend(friend)  # Attempt to add the same friend again
    assert len(test_human_user.friends) == initial_count


def test_add_invalid_friend(test_human_user: HumanUser):
    initial_count = len(test_human_user.friends)
    test_human_user.add_friend("not_a_user")  # Attempt to add invalid friend
    assert len(test_human_user.friends) == initial_count


def test_remove_friend(test_human_user: HumanUser):
    from pets.domainmodel.User import User
    from pathlib import Path
    from datetime import datetime

    friend = User(
        "removable_friend",
        "removable_friend.example.com",
        "hashed_password",
        Path(""),
        datetime.now(),
    )
    test_human_user.add_friend(friend)
    test_human_user.remove_friend(friend)
    assert friend not in test_human_user.friends


def test_remove_nonexistent_friend(test_human_user: HumanUser):
    from pets.domainmodel.User import User
    from pathlib import Path
    from datetime import datetime

    non_friend = User(
        "non_friend",
        "non_friend.example.com",
        "hashed_password",
        Path(""),
        datetime.now(),
    )
    initial_count = len(test_human_user.friends)
    test_human_user.remove_friend(non_friend)  # Attempt to remove non-friend
    assert len(test_human_user.friends) == initial_count


def test_remove_invalid_friend(test_human_user: HumanUser):
    initial_count = len(test_human_user.friends)
    test_human_user.remove_friend("not_a_user")  # Attempt to remove invalid friend
    assert len(test_human_user.friends) == initial_count
    from pets.domainmodel.User import User
    from pathlib import Path
    from datetime import datetime

    friend = User(
        "test_friend",
        "test_friend.example.com",
        "hashed_password",
        Path(""),
        datetime.now(),
    )
    test_human_user.add_friend(friend)
    assert friend in test_human_user.friends
    test_human_user.remove_friend(friend)
    assert friend not in test_human_user.friends
