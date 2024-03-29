import json
import six
from six import StringIO
from plone.app.textfield import RichTextValue
from z3c.form.interfaces import HIDDEN_MODE
from Products.Five.browser import BrowserView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.namedfile.interfaces import INamedFile
from plone.app.contenttypes.browser.folder import FolderView
from collective.easyform.interfaces import IFieldExtender
from collective.easyform.interfaces import IReCaptcha
from zope.i18n import translate
from .action import ACTION_DEFAULT_TITLE
from plone.restapi.serializer.converters import json_compatible
from collective.easyform.api import get_schema
from collections import OrderedDict
from .action import get_save_content_action
from .action import STORAGE_ID
from .utils import safe_nativestring
import csv


class SavedContentUtils(BrowserView):

    def has_saved_content(self):
        context = self.context
        if context.portal_type != 'EasyForm':
            return False
        action = get_save_content_action(context)
        if action is not None and getattr(context, STORAGE_ID, None):
            return True
        return False

    def saved_content_url(self):
        context = self.context
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
        fields = [schema[f] for f in schema]
        fields.sort(key=lambda f: f.order)
        for field in fields:
            if IReCaptcha.providedBy(field):
                continue
            field_name = field.__name__
            schema_fields[field_name] = safe_nativestring(field.title)
        # Use content values here to disallow exporting of content where the
        # user doesn't have view permission.
        for obj in self.context.contentValues():
            obj_dict = {}
            for field_name, field_title in schema_fields.items():
                value = getattr(obj, field_name, u'') or u''
                if isinstance(value, (str, (six.text_type, six.binary_type))):
                    value = safe_nativestring(value)
                elif isinstance(value, RichTextValue):
                    # Get string output and remove carriage returns
                    value = safe_nativestring(value.output).replace('&#13;', '')
                elif INamedFile.providedBy(value):
                    value = safe_nativestring(value.filename)
                elif isinstance(value, (list, tuple)):
                    value = '; '.join(safe_nativestring(v) for v in value)
                else:
                    context_json = json_compatible(value, obj)
                    if context_json is not None:
                        value = str(context_json)
                    else:
                        value = str(json_compatible(value))
                obj_dict[field_title] = value
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
