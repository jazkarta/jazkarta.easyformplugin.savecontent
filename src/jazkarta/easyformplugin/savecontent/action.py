import logging
from datetime import datetime
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent
from collective.easyform.actions import Action, ActionFactory
from collective.easyform.api import get_context
from plone.dexterity.utils import createContent, createContentInContainer
from plone.supermodel.exportimport import BaseHandler
from zope.interface import implementer
from Products.statusmessages.interfaces import IStatusMessage

from . import _
from .interfaces import IEasyformSaveContent

logger = logging.getLogger(__name__)


@implementer(IEasyformSaveContent)
class EasyformSaveContent(Action):
    """easyform action which saves data to a content object
    """

    def get_form(self):
        return get_context(self)

    def get_storage(self):
        form = self.get_form()
        storage = getattr(form, 'saved_form_entries', None)
        if storage is None:
            # We store the storage folder as an attribute of the non-container form object
            folder = createContent('jazkarta.efp.data_folder', id='saved_form_entries', title=u'Saved Form Entries')
            form.saved_form_entries = folder
            storage = form.saved_form_entries
            notify(ObjectAddedEvent(storage, form, 'saved_form_entries'))
        return storage

    def onSuccess(self, fields, request):
        """ TODO
        """
        content = self.create_content(fields)
        IStatusMessage(request).add(_(u'Your response has been saved.'))
        request.response.redirect(content.absolute_url())
        return ''

    def create_content(self, fields):
        storage = self.get_storage()
        content = createContentInContainer(
            storage, 'jazkarta.efp.saved_data_content',
            checkConstraints=False,
            **fields
        )
        return content


# Action factory used by the UI for adding a new easyform action
EasyformSaveContentAction = ActionFactory(
    EasyformSaveContent,
    _(u"label_easyformsavecontent_action", default=u"Save data as content"),
    "jazkarta.easyformplugin.savecontent.AddEasyformSaveContentActions",
)


# Supermodel handler for serializing the action configuration to an XML model
EasyformSaveContentHandler = BaseHandler(EasyformSaveContent)
