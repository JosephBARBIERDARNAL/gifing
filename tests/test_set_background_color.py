import pytest
from gifing import Gif


def test_set_background_color():
    gif = Gif(file_path=["image1.jpg", "image2.jpg"])
    gif.set_background_color((0, 0, 0))
    assert gif.background_color == (0, 0, 0)

    gif.set_background_color("red")
    assert gif.background_color == (255, 0, 0)