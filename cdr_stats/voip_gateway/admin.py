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

from django.contrib import admin
from django.utils.translation import gettext as _
from voip_gateway.models import Gateway, Provider


class GatewayAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Gateway Detail'), {
            'fields': ('name', 'description', 'addprefix', 'removeprefix',
                       'protocol', 'hostname', 'secondused', 'failover',
                       'addparameter', 'count_call', 'count_using',
                       'maximum_call', 'status', 'max_call_gateway'),
        }),
    )
    list_display = ('id', 'name', 'protocol', 'hostname', 'addprefix',
                    'removeprefix', 'secondused', 'count_call')
    list_display_links = ('name', )
    list_filter = ['protocol', 'hostname']
    ordering = ('id', )

admin.site.register(Gateway, GatewayAdmin)


class ProviderAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Provider Detail'), {
            # 'classes':('collapse', ),
            'fields': ('name', 'description', 'gateway', 'metric'),
        }),
    )
    list_display = ('id', 'name', 'gateway', 'metric', 'updated_date')
    list_display_links = ('name', )
    list_filter = ['gateway', 'metric']
    ordering = ('id', )

admin.site.register(Provider, ProviderAdmin)
