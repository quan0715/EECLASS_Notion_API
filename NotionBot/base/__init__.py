"""
base objct of the notion api, including  page database block
and each of the base object is inherent from Base class
"""
from .Page import Page
from .Database import Database
from .Block import Block
__all__ = ['Page', 'Database', 'Block']
