from StringIO import StringIO
from Products.Five.browser import BrowserView
from plone.app.layout.viewlets import ViewletBase
from collective.easyform.api import get_schema
from collections import OrderedDict
from .action import get_save_content_action
from .action import STORAGE_ID
import csv

try:
    unicode
except NameError:
    unicode = str


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
        return self.context.absolute_url() + '/' + STORAGE_ID


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


class ButtonViewlet(ViewletBase):
    def render(self):
        return """
        <a class="submit-widget button blue button-field submitting" href="%s">
            Download CSV
        </a>
        """ % (self.context.absolute_url() + "/download-csv")
