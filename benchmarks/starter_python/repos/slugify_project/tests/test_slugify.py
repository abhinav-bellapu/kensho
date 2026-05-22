from slugify import slugify


def test_basic_ascii():
    assert slugify("Hello World") == "hello-world"


def test_unicode_cafe():
    assert slugify("Café au lait") == "cafe-au-lait"
