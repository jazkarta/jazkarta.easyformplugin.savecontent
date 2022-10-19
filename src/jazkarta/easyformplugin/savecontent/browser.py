from StringIO import StringIO
from Products.Five.browser import BrowserView
from plone.app.layout.viewlets import ViewletBase
from collections import OrderedDict
from .content import EasyformSchemaBehaviorAssignment
from .action import get_save_content_action
from .action import STORAGE_ID
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
        return self.context.absolute_url() + '/' + STORAGE_ID


class CSVDownload(BrowserView):

    def __call__(self):
        items_dicts = []
        keys = OrderedDict()
        for obj in self.context.objectValues():
            behavior_assignment = EasyformSchemaBehaviorAssignment(obj)
            obj_dict = {}
            for field_name in behavior_assignment.schema():
                obj_dict[field_name] = getattr(obj, field_name)
                keys[field_name] = True
            items_dicts.append(obj_dict)
        output = StringIO()
        csv_writer = csv.DictWriter(output, keys.keys())
        csv_writer.writeheader()
        for item in items_dicts:
            csv_writer.writerow(item)
        self.request.response.setHeader("Content-type", "text/csv")
        self.request.response.setHeader("Content-Disposition", 'attachment; filename="%s.csv"' % behavior_assignment.find_form().title)
        return output.getvalue()


class ButtonViewlet(ViewletBase):
    def render(self):
        return """
        <a class="submit-widget button blue button-field submitting" href="%s">
            Download CSV
        </a>
        """ % (self.context.absolute_url() + "/download-csv")
