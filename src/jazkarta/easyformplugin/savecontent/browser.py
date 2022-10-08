from Products.Five.browser import BrowserView
from .action import get_save_content_action
from .action import STORAGE_ID


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
