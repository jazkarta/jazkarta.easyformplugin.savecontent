# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory
from collective.easyform.content import EasyForm

_ = MessageFactory("jazkarta.easyformplugin.savecontent")
STORAGE_ID = 'saved-form-entries'


# Monkey Patch in an __getitem__ method to allow five.intid to work
def easyform_get_item(self, key):
    if key == STORAGE_ID:
        storage = getattr(self, key, None)
        if storage is not None:
            return storage
    raise AttributeError(key)

if getattr(EasyForm, '__getitem__', None) is None:
    EasyForm.__getitem__ = easyform_get_item
