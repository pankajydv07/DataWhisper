from backend.intent import is_greeting, looks_like_data_question


def test_detects_greeting() -> None:
    assert is_greeting("hi")
    assert is_greeting("Hello!")


def test_detects_data_question() -> None:
    assert looks_like_data_question("What was total revenue last month?")


def test_rejects_non_data_smalltalk() -> None:
    assert not looks_like_data_question("Tell me a joke")
