# tests for the app

def test_math():
    assert 1 + 1 == 2

def test_string():
    assert "hello" + " " + "world" == "hello world"

def test_list():
    x = [1, 2, 3]
    x.append(4)
    assert len(x) == 4
