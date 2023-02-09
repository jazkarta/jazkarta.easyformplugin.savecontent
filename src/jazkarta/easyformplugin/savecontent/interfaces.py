from zope.interface import Interface
from zope.interface import implementer
from zope.interface.interface import InterfaceClass
from zope.interface.interface import TAGGED_DATA
from zope import schema
from collective.easyform.interfaces.actions import IAction
from collective.easyform.interfaces import IReCaptcha
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform.interfaces import OMITTED_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
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
    write_permission(title=u'jazkarta.easyformplugin.savecontent.ViewHiddenFields')


class IFormContentFolder(Interface):
    """Content object containing saved form data"""


class ISavedContentTitleChooser(Interface):
    """Adapter interface that generates a title for saved content."""


@implementer(IFormFieldProvider)
class DynamicSaveContentSchema(SchemaClass):
    """Importable class for dynamic schemas"""
    _InterfaceClass__attrs = ()
    _implied = {}
    __name__ = 'DynamicSaveContentSchema'

    def __init__(self, schema=None):
        if schema is not None:
            # Pull in private attributes of schema for new interface attrs
            # skip recaptcha fields
            attrs = schema._InterfaceClass__attrs
            attrs[TAGGED_DATA] = schema._Element__tagged_values
            InterfaceClass.__init__(
                self, self.__class__.__name__,
                (Interface,), attrs, None,
                self.__class__.__module__
            )

            # Mark hidden and server side fields as hidden
            hidden_fields = schema.queryTaggedValue('THidden') or {}
            server_side = schema.queryTaggedValue('serverSide') or {}
            write_perm_map = schema.queryTaggedValue(WRITE_PERMISSIONS_KEY) or {}
            read_perm_map = schema.queryTaggedValue(READ_PERMISSIONS_KEY) or {}
            for fnames in (hidden_fields, server_side):
                for fname in fnames:
                    if fnames[fname] is False:
                        continue
                    write_perm_map[fname] = u'jazkarta.easyformplugin.savecontent.EditHiddenFields'
                    read_perm_map[fname] = u'jazkarta.easyformplugin.savecontent.ViewHiddenFields'
            self.setTaggedValue(WRITE_PERMISSIONS_KEY, write_perm_map)
            self.setTaggedValue(READ_PERMISSIONS_KEY, read_perm_map)
            omitted = ((schema.queryTaggedValue(OMITTED_KEY) or []) +
                       [(Interface, k, 'true') for k in attrs
                        if IReCaptcha.providedBy(attrs[k])])
            self.setTaggedValue(OMITTED_KEY, omitted)
