# tests for the app

def test_math():
    """make sure basic math works"""
    assert 1 + 1 == 2


def test_string():
    """test string stuff"""
    assert "hello" + " " + "world" == "hello world"


def test_list():
    """test list operations"""
    x = [1, 2, 3]
    x.append(4)
    assert len(x) == 4
