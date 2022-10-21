from StringIO import StringIO
from Acquisition import aq_inner, aq_parent
from z3c.form.interfaces import HIDDEN_MODE
from Products.Five.browser import BrowserView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.app.contenttypes.browser.folder import FolderView
from collective.easyform.interfaces import IFieldExtender
from zope.i18n import translate
from .action import ACTION_DEFAULT_TITLE
from plone.app.layout.viewlets import ViewletBase
from collective.easyform.api import get_schema
from collections import OrderedDict
from .action import get_save_content_action
from .action import STORAGE_ID
import csv

try:
    from Products.CMFPlone.utils import safe_nativestring
except ImportError:
    # Not needed for Products.CMFPlone >= 5.2a1
    from Products.CMFPlone.utils import safe_encode
    from Products.CMFPlone.utils import safe_unicode

    import six

    def safe_nativestring(value, encoding='utf-8'):
        """Convert a value to str in py2 and to text in py3
        """
        if six.PY2 and isinstance(value, six.text_type):
            value = safe_encode(value, encoding)
        if not six.PY2 and isinstance(value, six.binary_type):
            value = safe_unicode(value, encoding)
        return value

try:
    unicode
except NameError:
    unicode = str


class SavedContentUtils(BrowserView):

    def has_saved_content(self):
        context = self.context
        if context.portal_type == 'jazkarta.efp.saved_data_content':
            context = aq_parent(aq_parent(aq_inner(context)))
        if context.portal_type != 'EasyForm':
            return False
        action = get_save_content_action(context)
        if action is not None and getattr(context, STORAGE_ID, None):
            return True
        return False

    def saved_content_url(self):
        context = self.context
        if context.portal_type == 'jazkarta.efp.saved_data_content':
            context = aq_parent(aq_parent(aq_inner(context)))
        return context.absolute_url() + '/' + STORAGE_ID

    def csv_download_url(self):
        return self.context.absolute_url() + '/' + STORAGE_ID + '/' + 'download-csv'


class SavedContentEditForm(DefaultEditForm):

    def updateWidgets(self):
        super(SavedContentEditForm, self).updateWidgets()
        for _, widget in self.widgets.items():
            efield = IFieldExtender(widget.field)
            if getattr(efield, "THidden", False) or widget.field.readonly:
                widget.mode = HIDDEN_MODE
                widget.ignoreRequest = False


class FormContentFolderListingView(FolderView):
    """Form submissions listing page with a customized template"""

    def Title(self):
        default_title = safe_nativestring(translate(ACTION_DEFAULT_TITLE))
        action = get_save_content_action(self.context)
        action_title = safe_nativestring(action.title)
        # Use customized action or folder title. If they are both default, then
        # include the form title.
        if action_title != default_title:
            return action_title
        folder_title = safe_nativestring(getattr(self.context, 'title', u''))
        if folder_title and folder_title != default_title:
            return folder_title
        return "{}: {}".format(self.context.aq_parent.Title(), default_title)


class CSVDownload(BrowserView):

    def __call__(self):
        form = self.context.aq_parent
        items_dicts = []
        schema_fields = OrderedDict()
        schema = get_schema(form)
        for field_name in schema:
            schema_fields[field_name] = schema.get(field_name).title
            if isinstance(schema_fields[field_name], unicode):
                schema_fields[field_name] = schema_fields[field_name].encode("utf-8")
        for obj in self.context.objectValues():
            obj_dict = {}
            for field_name, field_title in schema_fields.items():
                obj_dict[field_title] = getattr(obj, field_name, '')
                if isinstance(obj_dict[field_title], unicode):
                    obj_dict[field_title] = obj_dict[field_title].encode("utf-8")
            items_dicts.append(obj_dict)
        output = StringIO()
        csv_writer = csv.DictWriter(output, schema_fields.values())
        csv_writer.writeheader()
        for item in items_dicts:
            csv_writer.writerow(item)
        self.request.response.setHeader("Content-type", "text/csv; charset=utf-8")
        self.request.response.setHeader("Content-Disposition", 'attachment; filename="%s.csv"' % form.title)
        self.request.response.setHeader("Content-Length", str(output.tell()))
        return output.getvalue()
