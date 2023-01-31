import six

try:
    from Products.CMFPlone.utils import safe_nativestring
except ImportError:
    # Not needed for Products.CMFPlone >= 5.2a1
    from Products.CMFPlone.utils import safe_encode
    from Products.CMFPlone.utils import safe_unicode

    def safe_nativestring(value, encoding='utf-8'):
        """Convert a value to str in py2 and to text in py3
        """
        if six.PY2 and isinstance(value, six.text_type):
            value = safe_encode(value, encoding)
        if not six.PY2 and isinstance(value, six.binary_type):
            value = safe_unicode(value, encoding)
        return value
