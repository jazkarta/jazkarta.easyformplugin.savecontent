from datetime import datetime
from Acquisition import aq_chain, aq_parent
from zope.component import adapter
from zope.container.interfaces import INameChooser
from zope.interface import implementer
from zope.interface import alsoProvides
from zope.interface.declarations import Implements
from zope.globalrequest import getRequest
from collective.easyform.api import get_schema
from collective.easyform.interfaces import IEasyForm
from plone.app.content.namechooser import NormalizingNameChooser
from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.interfaces import IBehavior
from plone.dexterity.content import Item
from plone.dexterity.content import FTIAwareSpecification
from plone.dexterity.behavior import DexterityBehaviorAssignable
from plone.memoize import volatile
from plone.memoize import request
from .interfaces import IFormContentFolder
from .interfaces import IFormSaveContent


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
    __providedBy__ = FormAwareSpecification()


@implementer(IBehavior)
class EasyformSchemaBehaviorAssignment(object):
    title = u'Easyform Schema Behavior'
    description = u'Inherits schema from containing easyform'
    factory = None
    name = u'jazkara.easformplugins.savecontent'
    former_dotted_names = ''
    interface = marker = None

    def __init__(self, context):
        self.context = context
        schema = self.schema()
        if schema is not volatile._marker:
            self.interface = schema
            self.marker = schema

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
            alsoProvides(schema, IFormFieldProvider)
            # make sure we don't end up with a unicade prefix
            schema.__name__ = ''
            return schema
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
