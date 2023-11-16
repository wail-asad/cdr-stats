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

from django.utils.translation import gettext as _
from django_lets_go.utils import Choice


class NOTICE_TYPE(Choice):
    average_length_of_call = 1, _('average length of call').capitalize()
    answer_seize_ratio = 2, _('answer seize ratio').capitalize()
    blacklist_prefix = 3, _('blacklist prefix').capitalize()
    whitelist_prefix = 4, _('whitelist prefix').capitalize()
