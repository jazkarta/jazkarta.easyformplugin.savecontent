from zope.interface import Interface
from zope.interface import implementer
from zope import schema
from collective.easyform.interfaces.actions import IAction
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform.interfaces import WRITE_PERMISSIONS_KEY
from plone.autoform.directives import write_permission
from plone.supermodel.model import SchemaClass

from . import _


class IJazkartaEasyformpluginSaveContentLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IEasyformSaveContent(IAction):
    """Easyform action which saves data as content"""


@implementer(IFormFieldProvider)
class IFormSaveContent(Interface):
    """Content object containing saved form data"""

    title = schema.TextLine(
        title=_(u'Title'),
        description=_('Display title, editable by admins only.'),
        required=False,
    )
    write_permission(title=u'jazkarta.easyformplugin.savecontent.AddEasyformSaveContentActions')


class IFormContentFolder(Interface):
    """Content object containing saved form data"""


class ISavedContentTitleChooser(Interface):
    """Adapter interface that generates a title for saved content."""


@implementer(IFormFieldProvider)
class DynamicSaveContentSchema(SchemaClass):
    """Importable class for dynamic schemas"""
    _InterfaceClass__attrs = ()
    _implied = {}

    def __init__(self, schema=None):
        if schema is not None:
            self.__dict__ = schema.__dict__
            self.__name__ = self.__class__.__name__
            self.__module__ = self.__class__.__module__
            # Mark hidden and server side fields as hidden
            hidden_fields = schema.queryTaggedValue('THidden') or {}
            server_side = schema.queryTaggedValue('serverSide') or {}
            field_modes = schema.queryTaggedValue(WRITE_PERMISSIONS_KEY) or {}
            for fnames in (hidden_fields, server_side):
                for fname in fnames:
                    if fnames[fname] is False:
                        continue
                    field_modes[fname] = u'jazkarta.easyformplugin.savecontent.EditHiddenFields'
            schema.setTaggedValue(WRITE_PERMISSIONS_KEY, field_modes)
