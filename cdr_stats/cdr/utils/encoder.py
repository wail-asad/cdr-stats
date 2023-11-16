# -*- coding: utf-8 -*-

#
# This code is borrowed from django-cms
# https://raw.githubusercontent.com/divio/django-cms/develop/cms/utils/encoder.py
# Licensed as https://github.com/divio/django-cms/blob/develop/LICENSE
#

from django.utils.html import conditional_escape
from django.utils.encoding import force_str
from django.utils.functional import Promise
from django.core.serializers.json import DjangoJSONEncoder
from six import iteritems


class SafeJSONEncoder(DjangoJSONEncoder):
    def _recursive_escape(self, o, esc=conditional_escape):
        if isinstance(o, dict):
            return type(o)((esc(k), self._recursive_escape(v)) for (k, v) in iteritems(o))
        if isinstance(o, (list, tuple)):
            return type(o)(self._recursive_escape(v) for v in o)
        if type(o) is bool:
            return o
        try:
            return type(o)(esc(o))
        except (ValueError, TypeError):
            return self.default(o)

    def encode(self, o):
        value = self._recursive_escape(o)
        return super(SafeJSONEncoder, self).encode(value)

    def default(self, o):
        if isinstance(o, Promise):
            return force_str(o)
        return super(SafeJSONEncoder, self).default(o)
