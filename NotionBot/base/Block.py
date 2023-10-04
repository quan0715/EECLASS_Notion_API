from ..object import *
from .Base import *

class Block(Base):
    def __init__(self, bot, block_id):
        super().__init__(bot, block_id, 'block')
        self.children_url = f'{self.object_api}/children'


    # def update(self, data, **kwargs):
    #     return super().update(self.block_api, data)
