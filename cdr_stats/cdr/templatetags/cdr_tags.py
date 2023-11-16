#
# CDR-Stats License
# http://www.cdr-stats.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
from django import template
from django.utils.translation import gettext as _
from cdr.functions_def import get_hangupcause_name, get_switch_ip_addr
from django.utils.safestring import mark_safe
import json
from cdr.utils.encoder import SafeJSONEncoder
import re

register = template.Library()


@register.filter(name='get_switch_ip')
def get_switch_ip(id):
    """Tag is used to get switch name"""
    return get_switch_ip_addr(id)


@register.filter(name='hangupcause_name')
def hangupcause_name(id):
    """Tag is used to get hangupcause name"""
    return get_hangupcause_name(id)


@register.filter(name='hangupcause_name_with_title')
def hangupcause_name_with_title(id):
    """Tag is used to get hangupcause name with lowercase

    >>> hangupcause_name_with_title(10000)
    ''
    """
    try:
        val = get_hangupcause_name(id)
        t = re.sub("([a-z])'([A-Z])", lambda m: m.group(0).lower(), val.title())
        return re.sub("\d([A-Z])", lambda m: m.group(0).lower(), t)
    except:
        return ''


@register.filter(name='get_cost')
def get_cost(rate, billsec):
    try:
        cost = (float(rate) * float(float(billsec) / 60))
    except:
        cost = 0.0
    return str(round(cost, 4))


@register.simple_tag(name='cdr_details')
def cdr_details(cdr_id):
    """Create link to get cdr detail"""
    link = '<a href="#cdr-detail"  url="/cdr_detail/%s" class="cdr-detail" data-toggle="modal" data-controls-modal="cdr-detail" title="%s"><i class="fa fa-search"></i></a>' \
           % (cdr_id, _('cdr detail').capitalize())
    return link


@register.filter('json')
def json_filter(value):
    """
    Returns the JSON representation of ``value`` in a safe manner.
    """
    return mark_safe(json.dumps(value,
                                sort_keys=True,
                                indent=4,
                                cls=SafeJSONEncoder))
