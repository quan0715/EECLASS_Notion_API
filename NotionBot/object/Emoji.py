from .NotionObject import *


class Emoji(NotionObject):
    def __init__(self, emoji: str):
        super().__init__()
        self.emoji = emoji
        self.template = {"emoji": self.emoji}

    # def update(self, emoji) -> dict:
    #     self.emoji = emoji
    #     self.template["emoji"] = self.emoji
    #     return self.template
