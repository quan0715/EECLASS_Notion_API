from enum import Enum


class Colors:
    class Text(str, Enum):
        default = "default"
        gray = "gray"
        brown = "brown"
        orange = "orange"
        yellow = "yellow"
        green = "green"
        blue = "blue"
        purple = "purple"
        pink = "pink"
        red = "red"

    class Option(str, Enum):
        default = "default"
        gray = "gray"
        brown = "brown"
        orange = "orange"
        yellow = "yellow"
        green = "green"
        blue = "blue"
        purple = "purple"
        pink = "pink"
        red = "red"

    class Background(str, Enum):
        gray = "gray_background"
        brown = "brown_background"
        orange = "orange_background"
        yellow = "yellow_background"
        green = "green_background"
        blue = "blue_background"
        purple = "purple_background"
        pink = "pink_background"
        red = "red_background"