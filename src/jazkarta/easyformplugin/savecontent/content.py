from datetime import datetime
from Acquisition import aq_chain, aq_parent
from zope.component import adapter
from zope.container.interfaces import INameChooser
from zope.interface import implementer
from zope.interface.declarations import Implements
from zope.globalrequest import getRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from collective.easyform.api import get_schema
from collective.easyform.interfaces import IEasyForm
from plone import api
from plone.app.content.namechooser import NormalizingNameChooser
from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.interfaces import IBehavior
from plone.dexterity.content import Item
from plone.dexterity.content import FTIAwareSpecification
from plone.dexterity.behavior import DexterityBehaviorAssignable
from plone.memoize import volatile
from plone.memoize import request
from Products.CMFPlone.utils import safe_unicode
from .interfaces import IFormContentFolder
from .interfaces import IFormSaveContent
from .interfaces import ISavedContentTitleChooser
from .interfaces import DynamicSaveContentSchema


def schema_key(func, behavior):
    key = 'easyform.schema.cache'
    if behavior.context and getattr(behavior.context, 'id', None):
        # incorporate the form id from the response id into the cache key
        key += '.' + behavior.context.id.split('-savecontent-response-')[0]
    return key


class FormAwareSpecification(FTIAwareSpecification):
    """The schema cache is too aggressive for this usecase, we need to
    fetch the form schema dynamically since we can't always acquire it."""

    def __get__(self, inst, cls=None):
        spec = super(FormAwareSpecification, self).__get__(inst, cls)
        if inst is None:
            return spec
        behavior = EasyformSchemaBehaviorAssignment(inst).interface
        if behavior:
            spec = list(spec)
            spec.append(behavior)
            return Implements(*spec)
        else:
            return spec


@implementer(IFormSaveContent)
class FormSaveContent(Item):

    def __conform__(self, proto):
        """We conform to all dynamic schema interfaces"""
        if getattr(proto, '__name__', None) == 'DynamicSaveContentSchema':
            return self
        return None


@implementer(IBehavior)
class EasyformSchemaBehaviorAssignment(object):
    title = u'Easyform Schema Behavior'
    description = u'Inherits schema from containing easyform'
    factory = None
    name = u'jazkara.easformplugins.savecontent'
    former_dotted_names = ''
    marker = None
    interface = IFormFieldProvider

    def __init__(self, context):
        self.context = context
        schema = self.schema()
        if schema is not volatile._marker:
            self.interface = schema
        # else:
        #     self.interface = DynamicSaveContentSchema()

    def find_form(self):
        for parent in aq_chain(self.context):
            if IEasyForm.providedBy(parent):
                return parent

    @request.cache(schema_key, 'self._get_request()')
    def schema(self):
        # we cache the schema once we have it, because we don't always have an
        # acquisition path from which to find it
        form = self.find_form()
        if form is not None:
            schema = get_schema(self.find_form())
            return DynamicSaveContentSchema(schema)
        return volatile._marker

    def _get_request(self):
        return getRequest()


@adapter(IFormSaveContent)
class EasyFormSchemaBehaviorAssignment(DexterityBehaviorAssignable):

    def enumerateBehaviors(self):
        yield EasyformSchemaBehaviorAssignment(self.context)
        for behavior in super(EasyFormSchemaBehaviorAssignment, self).enumerateBehaviors():
            yield behavior


@implementer(INameChooser)
@adapter(IFormContentFolder)
class FormContentNameChooser(NormalizingNameChooser):

    def chooseName(self, name, obj):
        if not name:
            name = aq_parent(self.context).getId() + '-savecontent-response-' + datetime.now().isoformat()
        return super(FormContentNameChooser, self).chooseName(name, obj)


NAME_FIELDS = [
    'submitter-name', 'submitter_name',
    'name', 'fullname', 'full_name', 'full-name',
    ('first-name', 'last-name'), ('first_name', 'last_name'),
    ('firstname', 'lastname'), ('first', 'last'),
]
USER_ID_FIELDS = [
    'user', 'user_id', 'userid',
    'surveyed-user-id', 'surveyed_user_id',
    'creators'
]
OBJECT_FIELDS = [
    'surveyed-object-uid', 'surveyed_object_uid',
    'object_uid', 'object_uid',
]


def name_for_userid(userid):
    user = api.user.get(userid=userid)
    if user:
        try:
            return safe_unicode(user.getProperty('fullname', None) or userid)
        except ValueError:
            return


@implementer(ISavedContentTitleChooser)
@adapter(IFormSaveContent, IDefaultBrowserLayer)
def chooseTitle(obj, request):
    title = []

    for name in NAME_FIELDS:
        if isinstance(name, tuple):
            name_val = u' '.join([getattr(obj, n, u'') for n in name]).strip()
        else:
            name_val = getattr(obj, name, None)
        if name_val:
            title.append(safe_unicode(name_val))
            break

    if not title:
        for user_key in USER_ID_FIELDS:
            userids = getattr(obj, user_key, None)
            if not userids:
                continue
            if not isinstance(userids, (list, tuple)):
                userids = (userids,)
            for userid in userids:
                name = name_for_userid(userid)
                if name:
                    title.append(name)
                    break

    for fname in OBJECT_FIELDS:
        uid = getattr(obj, fname, None)
        if uid:
            brains = api.portal.get_tool('portal_catalog').unrestrictedSearchResults(UID=uid)
            if brains:
                title.append(u'-')
                title.append(safe_unicode(brains[0].Title))

    # Add surveyed date to title
    if getattr(obj, 'creation_date', None):
        dt = obj.creation_date
        if dt:
            title.append(u'-')
            title.append(safe_unicode(dt.strftime('%Y-%m-%d')))

    return u' '.join(title)
