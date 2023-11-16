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

from django.utils.translation import gettext_lazy as _
from django_lets_go.utils import Choice
from django.db import models


class STRING_SEARCH_TYPE_LIST(models.IntegerChoices):
    EQUALS = 1, _('Equals')
    BEGINS_WITH = 2, _('Begins')
    CONTAINS = 3, _('Contains')
    ENDS_WITH = 4, _('Ends')


class CDR_COLUMN_NAME(models.TextChoices):
    call_date = _('call-date')
    clid = _('CLID')
    destination = _('destination')
    duration = _('duration')
    bill = _('billsec')
    hangup_cause = _('hangup cause')
    account = _('account')
    buy_rate = _('buy rate')
    buy_cost = _('buy cost')
    sell_rate = _('sell rate')
    sell_cost = _('sell cost')


class Export_choice(models.TextChoices):
    CSV = 'csv', _('CSV')
    XLS = 'xls', _('XLS')
    JSON = 'json', _('JSON')


class COMPARE_WITH(models.IntegerChoices):
    previous_days = 1, _('previous days').title()
    previous_weeks = 2, _('previous weeks').title()


CDR_FIELD_LIST = (
    'caller_id_number',
    'caller_id_name',
    'destination_number',
    'duration',
    'billsec',
    'hangup_cause_id',
    'direction',
    'uuid',
    'remote_media_ip',
    'start_uepoch',
    'answer_uepoch',
    'end_uepoch',
    'mduration',
    'billmsec',
    'read_codec',
    'write_codec',
    'accountcode',
)

CDR_FIELD_LIST_NUM = [
    (x, 'column-' + str(x)) for x in range(1, len(CDR_FIELD_LIST) + 1)
]
