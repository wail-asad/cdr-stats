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
from django.db import models
from django.utils.translation import gettext_lazy as _
from country_dialcode.models import Prefix
from voip_gateway.models import Provider
from voip_billing.function_def import prefix_allowed_to_call
from django_lets_go.intermediate_model_base_class import Model
from django.db import connection


LCR_TYPE = (
    (0, 'LCR'),
    (1, 'LCD'),
)


class VoIPPlan(Model):

    """
    VoIPPlan

    VoIPPlans are associated to your clients, this defines the rate at which
    the VoIP calls are sold to your clients.
    A VoIPPlan is a collection of VoIPRetailPlans, you can have 1 or more
    VoIPRetailPlans associated to the VoIPPlan

    A client has a single VoIPPlan,
    VoIPPlan has many VoIPRetailPlans.
    VoIPRetailPlan has VoIPRetailRates

    The LCR system will route the VoIP via the lowest cost carrier.
    """
    name = models.CharField(unique=True, max_length=255, verbose_name=_('name'),
                            help_text=_("enter plan name"))
    pubname = models.CharField(max_length=255, verbose_name=_('publish name'),
                               help_text=_("enter publish name"))
    lcrtype = models.IntegerField(choices=LCR_TYPE, verbose_name=_('LCR type'),
                                  help_text=_("select LCR type"))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'voip_plan'
        verbose_name = _("VoIP plan")
        verbose_name_plural = _("VoIP plans")

    def __unicode__(self):
        return '[%s] %s' % (self.id, self.name)


class BanPlan(models.Model):

    """
    BanPlan

    List of Ban Plan which are linked to VoIP Plan
    """
    name = models.CharField(unique=True, max_length=255, verbose_name=_('name'),
                            help_text=_("enter ban plan name"))
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    voip_plan = models.ManyToManyField(VoIPPlan, through='VoIPPlan_BanPlan')

    class Meta:
        db_table = u'voipbilling_banplan'
        verbose_name = _("ban plan")
        verbose_name_plural = _("ban plans")

    def __unicode__(self):
        return "%s" % (self.name)


class VoIPPlan_BanPlan(models.Model):

    """
    VoIPPlan_BanPlan

    OnetoMany relationship between VoIPPlan & BanPlan
    """
    voipplan = models.ForeignKey(VoIPPlan,on_delete=models.PROTECT, related_name='voip_plan1')
    banplan = models.ForeignKey(BanPlan,on_delete=models.PROTECT, related_name='ban_plan2')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u'voipplan_banplan'

    def __unicode__(self):
        return "%s" % (self.banplan)


class BanPrefix(models.Model):

    """
    BanPrefix

    Ban prefixes are linked to Ban plan & VoIP with these prefix
    will not be authorized to send.
    """
    ban_plan = models.ForeignKey(BanPlan,on_delete=models.PROTECT, verbose_name=_('ban plan'), help_text=_("select ban plan"))
    prefix = models.ForeignKey(Prefix,on_delete=models.PROTECT, verbose_name=_('prefix'), help_text=_("select prefix"))
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'voipbilling_ban_prefix'
        verbose_name = _("ban prefix")
        verbose_name_plural = _("ban prefixes")

    def __unicode__(self):
        return "%s" % (self.ban_plan)

    def prefix_with_name(self):
        """
        Return prefix with name
        on Ban Prefix Listing (changelist_view)
        """
        if self.prefix is None:
            return ""
        else:
            return "[%d] - %s" % (self.prefix.prefix, self.prefix.destination)
    prefix_with_name.short_description = _('prefix')


class VoIPRetailPlan(Model):

    """
    VoIPRetailPlan

    This contains the VoIPRetailRates to retail to the customer. these plans are
    associated to the VoIPPlan with a ManyToMany relation.
    It defines the costs at which we sell the VoIP calls to clients.

    VoIPRetailPlan will then contain a set of VoIPRetailRates which will define
    the cost of sending a VoIP call to each destination.
    The system can have several VoIPRetailPlans, but only the ones associated to
    the VoIPplan will be used by the client.
    """
    name = models.CharField(max_length=255, verbose_name=_('name'), help_text=_("enter plan name"))
    description = models.TextField(verbose_name=_('description'), null=True, blank=True,
                                   help_text=_("short description about Plan"))
    metric = models.IntegerField(default=10, verbose_name=_('metric'), help_text=_("enter metric in digit"))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))
    updated_date = models.DateTimeField(auto_now=True)
    voip_plan = models.ManyToManyField(VoIPPlan, through='VoIPPlan_VoIPRetailPlan')

    class Meta:
        db_table = u'voip_retail_plan'
        verbose_name = _("retail plan")
        verbose_name_plural = _("retail plans")

    def __unicode__(self):
        return "%s" % (self.name)


class VoIPPlan_VoIPRetailPlan(models.Model):

    """
    VoIPPlan_VoIPRetailPlan

    ManytoMany relationship between VoIPPlan & VoIPRetailPlan
    """
    voipretailplan = models.ForeignKey(VoIPRetailPlan,on_delete=models.PROTECT, related_name='VoIP_Retail_Plan')
    voipplan = models.ForeignKey(VoIPPlan,on_delete=models.PROTECT, related_name='VoIP_Plan')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u'voipplan_voipretailplan'

    def __unicode__(self):
        return "%s" % (self.voipplan)


class VoIPRetailRate(models.Model):

    """
    VoIPRetailRate

    A single VoIPRetailRate consists of a retail rate and prefix at which you
    want to use to sell a VoIP Call to a particular destination.
    VoIPRetailRates are grouped by VoIPRetailPlan, which will be then in turn be
    associated to a VoIPPlan
    """
    voip_retail_plan_id = models.ForeignKey(VoIPRetailPlan,on_delete=models.PROTECT, db_column="voip_retail_plan_id",
                                            verbose_name=_("retail plan"),
                                            help_text=_("select retail plan"))
    prefix = models.ForeignKey(Prefix,on_delete=models.PROTECT, db_column="prefix", verbose_name=_("prefix"),
                               help_text=_("select prefix"))
    retail_rate = models.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name=_("rate"),
                                      help_text=_("enter Rate"))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_("date"))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'voip_retail_rate'
        verbose_name = _("retail rate")
        verbose_name_plural = _("retail rates")

    def voip_retail_plan_name(self):
        """
        Return Retail Plan name
        on Retail Rate listing (changelist_view)
        """
        if self.voip_retail_plan_id is None:
            return ""
        else:
            return self.voip_retail_plan_id.name
    voip_retail_plan_name.short_description = _("retail plan")

    def prefix_with_name(self):
        """
        Return prefix with name
        on Retail Rate listing (changelist_view)
        """
        if self.prefix is None:
            return ""
        else:
            return "[%d] - %s" % (self.prefix.prefix, self.prefix.destination)
    prefix_with_name.short_description = _('prefix')


class VoIPCarrierPlan(Model):

    """
    VoIPCarrierPlan

    Once the retail price is defined by the VoIPPlan, VoIPRetailPlans and
    VoIPRetailRates, we also need to know which is the best route to send
    the VoIP how much it will cost, and which VoIP Gateway to use.

    VoIPCarrierPlan is linked to the VoIP Plan, so once we found how to sell
    the service to the client, we need to look at which carrier (Provider)
    we want to use, The VoIPCarrierPlan defines this.

    The system can have several VoIPCarrierPlans, but only the one associated to
    the VoIPRetailPlan-VoIPPlan will be used to connect the VoIP of
    the client.
    """
    name = models.CharField(max_length=255, verbose_name=_("name"),
                            help_text=_("enter plan name"))
    description = models.TextField(verbose_name=_("description"),
                                   null=True, blank=True,
                                   help_text=_("short description about Plan"))
    metric = models.IntegerField(default=10, verbose_name=_("metric"),
                                 help_text=_("enter metric in digit"))
    callsent = models.IntegerField(null=True, blank=True,
                                   verbose_name=_("message sent"))
    voip_provider_id = models.ForeignKey(Provider,on_delete=models.PROTECT, db_column="voip_provider_id",
                                         verbose_name=_("provider"),
                                         help_text=_("select provider"))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_("date"))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'voip_carrier_plan'
        verbose_name = _("carrier plan")
        verbose_name_plural = _("carrier plans")

    def __unicode__(self):
        return "%s" % (self.name)


class VoIPCarrierRate(models.Model):

    """
    VoIPCarrierRate

    The VoIPCarrierRates are a set of all the carrier rate and prefix that
    will be used to purchase the VoIP from your carrier,
    VoIPCarrierRates are grouped by VoIPCarrierPlan, which will be then
    associated to a VoIPRetailPlan
    """
    voip_carrier_plan_id = models.ForeignKey(VoIPCarrierPlan,on_delete=models.PROTECT, db_column="voip_carrier_plan_id",
                                             verbose_name=_("carrier plan"),
                                             help_text=_("select carrier plan"))
    prefix = models.ForeignKey(Prefix,on_delete=models.PROTECT, db_column="prefix", verbose_name=_("prefix"),
                               help_text=_("select prefix"))
    carrier_rate = models.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name=_("rate"),
                                       help_text=_("enter rate"))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_("date"))
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'voip_carrier_rate'
        verbose_name = _("carrier rate")
        verbose_name_plural = _("carrier rates")

    def voip_carrier_plan_name(self):
        """
        Return Carrier Plan name
        on Carrier Rate listing (changelist_view)
        """
        if self.voip_carrier_plan_id is None:
            return ""
        else:
            return self.voip_carrier_plan_id.name
    voip_carrier_plan_name.short_description = _("carrier plan")

    def prefix_with_name(self):
        """
        Return prefix with name
        on Carrier Rate listing (changelist_view)
        """
        if self.prefix is None:
            return ""
        else:
            return "[%d] - %s" % (self.prefix.prefix, self.prefix.destination)
    prefix_with_name.short_description = _("prefix")


class VoIPPlan_VoIPCarrierPlan(models.Model):

    """
    VoIPPlan_VoIPCarrierPlan

    ManytoMany relationship between VoIPPlan & VoIPCarrierPlan
    """
    voipcarrierplan = models.ForeignKey(VoIPCarrierPlan,on_delete=models.PROTECT, related_name='carrier_plan')
    voipplan = models.ForeignKey(VoIPPlan,on_delete=models.PROTECT, related_name='voip_plan')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u'voipplan_voipcarrierplan'

    def __unicode__(self):
        return "%s" % (self.voipplan)


def find_rates(voipplan_id, dialcode, sort_field, order):
    """
    function to retrieve list of rates belonging to a voipplan
    """
    cursor = connection.cursor()

    # variables used for sorting
    extension_query = ''

    if sort_field == 'prefix':
        sort_field = 'voip_retail_rate.prefix'
    if sort_field == 'retail_rate':
        sort_field = 'minrate'
    if sort_field == 'destination':
        sort_field = 'dialcode_prefix.destination'
    if sort_field:
        extension_query = "ORDER BY " + sort_field + ' ' + order

    cursor = connection.cursor()
    if dialcode:
        sqldialcode = str(dialcode) + '%'
        sql_statement = (
            "SELECT voip_retail_rate.prefix, "
            "Min(retail_rate) as minrate, dialcode_prefix.destination "
            "FROM voip_retail_rate "
            "INNER JOIN voipplan_voipretailplan "
            "ON voipplan_voipretailplan.voipretailplan_id = "
            "voip_retail_rate.voip_retail_plan_id "
            "LEFT JOIN dialcode_prefix ON dialcode_prefix.prefix = "
            "voip_retail_rate.prefix "
            "WHERE voipplan_id=%s "
            "AND CAST(voip_retail_rate.prefix AS TEXT) LIKE %s "
            "GROUP BY voip_retail_rate.prefix, dialcode_prefix.destination "
            + extension_query)

        cursor.execute(sql_statement, [voipplan_id, sqldialcode])
    else:
        sql_statement = (
            "SELECT voip_retail_rate.prefix, "
            "Min(retail_rate) as minrate, dialcode_prefix.destination "
            "FROM voip_retail_rate "
            "INNER JOIN voipplan_voipretailplan "
            "ON voipplan_voipretailplan.voipretailplan_id = "
            "voip_retail_rate.voip_retail_plan_id "
            "LEFT JOIN dialcode_prefix ON dialcode_prefix.prefix = "
            "voip_retail_rate.prefix "
            "WHERE voipplan_id=%s "
            "GROUP BY voip_retail_rate.prefix, dialcode_prefix.destination "
            + extension_query)

        cursor.execute(sql_statement, [voipplan_id])

    row = cursor.fetchall()
    result = []
    for record in row:
        # Not banned Prefix
        allowed = prefix_allowed_to_call(record[0], voipplan_id)
        if allowed:
            modrecord = {}
            modrecord['prefix'] = record[0]
            modrecord['retail_rate'] = record[1]
            modrecord['prefix__destination'] = record[2]
            result.append(modrecord)
    return result
