from markdown_links import extract_links


def test_no_links():
    assert extract_links("plain text") == []


def test_single_link():
    assert extract_links("see [docs](https://example.com/docs)") == [
        ("docs", "https://example.com/docs")
    ]


def test_two_adjacent_links():
    text = "[a](1)[b](2)"
    assert extract_links(text) == [("a", "1"), ("b", "2")]


def test_multiple_links_in_sentence():
    text = "Read [one](1) and [two](2) for details."
    assert extract_links(text) == [("one", "1"), ("two", "2")]


def test_link_with_spaces_in_label():
    assert extract_links("[hello world](x)") == [("hello world", "x")]


def test_three_links():
    text = "[x](a) then [y](b) and [z](c)"
    assert extract_links(text) == [("x", "a"), ("y", "b"), ("z", "c")]
