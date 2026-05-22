from binary_search import binary_search


def test_empty():
    assert binary_search([], 1) == -1


def test_single_match():
    assert binary_search([5], 5) == 0


def test_single_miss():
    assert binary_search([5], 3) == -1


def test_first_element():
    assert binary_search([1, 3, 5, 7, 9], 1) == 0


def test_last_element():
    assert binary_search([1, 3, 5, 7, 9], 9) == 4


def test_middle_element():
    assert binary_search([1, 3, 5, 7, 9], 5) == 2


def test_missing_between():
    assert binary_search([1, 3, 5, 7, 9], 4) == -1
