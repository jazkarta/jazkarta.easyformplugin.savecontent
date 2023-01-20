import logging
from lxml import etree
from zope.component import adapter
from zope.component import subscribers
from zope.event import notify
from zope.lifecycleevent import IObjectMovedEvent
from zope.lifecycleevent import ObjectAddedEvent
from zope.schema import getFieldsInOrder
from collective.easyform.actions import Action, ActionFactory
from collective.easyform.api import get_actions
from collective.easyform.api import get_context
from collective.easyform.interfaces import IEasyForm
from plone.dexterity.utils import createContent, createContentInContainer
from plone.supermodel import serializeSchema
from plone.supermodel.exportimport import BaseHandler
from zope.component import queryMultiAdapter
from zope.interface import implementer
from Products.statusmessages.interfaces import IStatusMessage

from . import _
from .interfaces import IEasyformSaveContent
from .interfaces import ISavedContentTitleChooser

logger = logging.getLogger(__name__)

STORAGE_ID = 'saved-form-entries'

# Add this to ensure we get a translation
ACTION_DEFAULT_TITLE = _(
    u'default_adapter_title',
    default=u'Save Data as Content',
)

DEFAULT_ACTION_SCHEMA = u'''
    <field name="save_data_as_content" type="jazkarta.easyformplugin.savecontent.action.EasyformSaveContent">
      <title>{}</title>
    </field>
'''


@implementer(IEasyformSaveContent)
class EasyformSaveContent(Action):
    """easyform action which saves data to a content object
    """

    def get_form(self):
        return get_context(self)

    def get_storage(self):
        form = self.get_form()
        storage = getattr(form, STORAGE_ID, None)
        if storage is None:
            # We store the storage folder as an attribute of the non-container form object
            folder = createContent('jazkarta.efp.data_folder', id=STORAGE_ID, title=self.title or u'Saved Form Entries')
            setattr(form, STORAGE_ID, folder)
            storage = getattr(form, STORAGE_ID)
            notify(ObjectAddedEvent(storage, form, STORAGE_ID))
        return storage

    def onSuccess(self, fields, request):
        """ TODO
        """
        content = self.create_content(fields)
        if not getattr(content, 'title', None):
            try:
                title = queryMultiAdapter((content, request), ISavedContentTitleChooser)
                if title:
                    content.title = title
            except Exception:
                logger.exception('Error generating title for {}'.format(content.absolute_url()))
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


def get_save_content_action(form):
    actions_schema = get_actions(form)
    actions = getFieldsInOrder(actions_schema)
    for name, action in actions:
        if IEasyformSaveContent.providedBy(action):
            return action


def add_action_to_form(form, title=ACTION_DEFAULT_TITLE):
    actions_model = serializeSchema(get_actions(form))
    parser = etree.XMLParser(remove_blank_text=True)
    model = etree.fromstring(actions_model, parser)
    schema = model.find("{http://namespaces.plone.org/supermodel/schema}schema")
    action_schema = DEFAULT_ACTION_SCHEMA.format(title)
    action_el = etree.fromstring(action_schema)
    schema.append(action_el)
    updated_model = etree.tostring(model, pretty_print=True)
    form.actions_model = updated_model
    form.notifyModified()
    action = get_save_content_action(form)
    return action


@adapter(IEasyForm, IObjectMovedEvent)
def handle_form_moved(obj, event):
    """The form isn't a folder so it doesn't dispatch move events to
    sub-objects.  We need to explicitly re-dispatch those events to the
    storage folder."""
    action = get_save_content_action(obj)
    if action is None:
        return
    storage = getattr(obj, STORAGE_ID, None)
    if storage is None:
        return
    # Iterate over all subscribers on the saved content storage
    for ignored in subscribers((storage, event), None):
        pass
