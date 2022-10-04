from zope.interface import Interface
from collective.easyform.interfaces.actions import IAction
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from . import _


class IJazkartaEasyformpluginSaveContentLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IEasyformSaveContent(IAction):
    """Easyform action which saves data as content"""


class IFormSaveContent(Interface):
    """Content object containing saved form data"""


class IFormContentFolder(Interface):
    """Content object containing saved form data"""
