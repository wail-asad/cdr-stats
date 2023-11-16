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

from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.template.context import RequestContext
from django.utils.translation import gettext as _
# from django.conf import settings
from django.db.models import Count
from cdr_alert.models import Alarm, Blacklist, Whitelist, AlarmReport
from cdr_alert.constants import ALARM_COLUMN_NAME, ALARM_REPORT_COLUMN_NAME
from cdr_alert.forms import AlarmForm, BWCountryForm, BWPrefixForm, AlarmReportForm
from cdr_alert.tasks import run_alarm
from cdr_alert.constants import ALERT_CONDITION, PERIOD
from django_lets_go.common_functions import getvar, get_pagination_vars, validate_days
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import logging

redirect_url_alarm = '/alert/'


@permission_required('cdr_alert.alarm_settings', login_url='/')
@login_required
def alarm_list(request):
    """Alarm list for the logged in user

    **Attributes**:

        * ``template`` - cdr_alert/alert_list.html

    **Logic Description**:

        * List all alarms which belong to the logged in user.
    """
    sort_col_field_list = ['id', 'name', 'period', 'type', 'alert_condition',
                           'alert_value', 'status', 'updated_date']
    page_data = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')
    alarm_list = Alarm.objects.filter(user=request.user).order_by(page_data['sort_order'])
    data = {
        'msg': request.session.get('msg'),
        'error_msg': request.session.get('error_msg'),
        'rows': alarm_list,
        'total_count': alarm_list.count(),
        'ALARM_COLUMN_NAME': ALARM_COLUMN_NAME,
        'col_name_with_order': page_data['col_name_with_order'],
        'up_icon': '<i class="glyphicon glyphicon-chevron-up"></i>',
        'down_icon': '<i class="glyphicon glyphicon-chevron-down"></i>'
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render('cdr_alert/alarm/list.html', data, context_instance=RequestContext(request))


@permission_required('cdr_alert.add_alarm', login_url='/')
@login_required
def alarm_add(request):
    """Add new Alarm for the logged in user

    **Attributes**:

        * ``form`` - AlarmForm
        * ``template`` - cdr_alert/alarm/change.html

    **Logic Description**:

        * Add a new Alarm which will belong to the logged in user
          via the AlarmForm & get redirected to the Alarm list
    """
    form = AlarmForm(request.POST or None)
    if form.is_valid():
        form.save(user=request.user)
        form.save()
        request.session["msg"] = _('"%(name)s" added.') % {'name': request.POST['name']}
        return HttpResponseRedirect(redirect_url_alarm)

    data = {
        'form': form,
        'action': 'add',
    }
    return render('cdr_alert/alarm/change.html', data, context_instance=RequestContext(request))


@permission_required('cdr_alert.alarm_test', login_url='/')
@login_required
def alarm_test(request, object_id):
    """Test a alarm for a logged in user

    **Attributes**:

        * ``object_id`` - Selected alarm object

    **Logic Description**:

        * Test selected the alarm from the alarm list
    """
    alarm_data = {}
    alarm_obj = get_object_or_404(Alarm, pk=object_id, user=request.user)

    alarm_data = run_alarm(alarm_obj, logging)
    if alarm_data['current_value'] is not None and alarm_data['previous_value'] is not None:
        if (alarm_obj.alert_condition != ALERT_CONDITION.IS_LESS_THAN or
                alarm_obj.alert_condition != ALERT_CONDITION.IS_GREATER_THAN):
            alarm_data['diff'] = round(abs(alarm_data['current_value'] - alarm_data['previous_value']), 2)

        if (alarm_obj.alert_condition == ALERT_CONDITION.PERCENTAGE_DECREASE_BY_MORE_THAN or
                alarm_obj.alert_condition == ALERT_CONDITION.PERCENTAGE_INCREASE_BY_MORE_THAN):
            avg = (alarm_data['current_value'] + alarm_data['previous_value']) / 2
            avg = avg if avg != 0 else 1
            alarm_data['percentage'] = round(alarm_data['diff'] / avg * 100, 2)

    data = {
        'alarm_obj': alarm_obj,
        'alarm_data': alarm_data,
        'ALERT_CONDITION': ALERT_CONDITION,
        'PERIOD': PERIOD,
    }
    return render('cdr_alert/alarm/alarm_testing.html', data, context_instance=RequestContext(request))


@permission_required('cdr_alert.delete_alarm', login_url='/')
@login_required
def alarm_del(request, object_id):
    """Delete a alarm for a logged in user

    **Attributes**:

        * ``object_id`` - Selected alarm object
        * ``object_list`` - Selected alarm objects

    **Logic Description**:

        * Delete selected the alarm from the alarm list
    """
    if int(object_id) != 0:
        # When object_id is not 0
        alarm = get_object_or_404(Alarm, pk=object_id, user=request.user)

        # 1) delete alarm
        request.session["msg"] = _('"%(name)s" is deleted.') % {'name': alarm.name}
        alarm.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        try:
            # 1) delete alarm
            alarm_list = Alarm.objects.filter(user=request.user).extra(where=['id IN (%s)' % values])
            if alarm_list:
                request.session["msg"] = _('%(count)s alarm(s) are deleted.') % {'count': alarm_list.count()}
                alarm_list.delete()
        except:
            raise Http404

    return HttpResponseRedirect(redirect_url_alarm)


@permission_required('cdr_alert.change_alarm', login_url='/')
@login_required
def alarm_change(request, object_id):
    """Update/Delete Alarm for the logged in user

    **Attributes**:

        * ``object_id`` - Selected alarm object
        * ``form`` - AlarmForm
        * ``template`` - cdr_alert/alarm/change.html

    **Logic Description**:

        * Update/delete selected alarm from the alarm list
          via alarmForm & get redirected to alarm list
    """
    alarm = get_object_or_404(Alarm, pk=object_id, user=request.user)
    form = AlarmForm(request.POST or None, instance=alarm)
    if request.method == 'POST':
        if request.POST.get('delete'):
            alarm_del(request, object_id)
            return HttpResponseRedirect(redirect_url_alarm)
        else:
            if form.is_valid():
                form.save()
                request.session["msg"] = _('"%(name)s" is updated.') % {'name': request.POST['name']}
                return HttpResponseRedirect(redirect_url_alarm)
    data = {
        'form': form,
        'action': 'update',
    }
    return render('cdr_alert/alarm/change.html', data, context_instance=RequestContext(request))


def last_seven_days_report(request, kwargs):
    comp_days = 7
    from_date = datetime.today()
    from_day = validate_days(from_date.year, from_date.month, from_date.day)
    end_date = datetime(from_date.year, from_date.month, from_day)
    start_date = end_date + relativedelta(days=-comp_days)
    start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, 0)
    end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, 999999)

    if start_date and end_date:
        kwargs['daterun__range'] = (start_date, end_date)

    select_data = {"daterun": "SUBSTR(CAST(daterun as CHAR(30)),1,10)"}
    alarm_data = AlarmReport.objects.extra(select=select_data)\
        .values('daterun')\
        .filter(**kwargs)\
        .annotate(Count('daterun'))\
        .order_by('-daterun')

    total_data = {}
    total_alert = 0
    charttype = "lineWithFocusChart"
    chartdata = {"x": []}
    for doc in alarm_data:
        daterun = str(doc['daterun'])
        graph_day = datetime(int(daterun[0:4]), int(daterun[5:7]), int(daterun[8:10]),
                             0, 0, 0, 0)
        dt = int(1000 * time.mktime(graph_day.timetuple()))

        if dt in total_data:
            total_data[dt]['alert_count'] += int(doc['daterun__count'])
        else:
            total_data[dt] = {
                'alert_count': int(doc['daterun__count'])
            }

        total_alert += int(doc['daterun__count'])

    # sorting on date col
    total_data = sorted(total_data.items(), key=lambda k: k[0])

    xdata = [i[0] for i in total_data]
    ydata = [i[1]['alert_count'] for i in total_data]

    tooltip_date = "%d %b %Y %H:%M %p"
    extra_serie = {"tooltip": {"y_start": "", "y_end": ""},
                   "date_format": tooltip_date}
    chartdata = {
        'x': xdata,
        'name1': 'Alert', 'y1': ydata, 'extra1': extra_serie,
    }

    data = {
        'start_date': start_date,
        'end_date': end_date,
        'total_data': total_data,
        'total_alert': total_alert,
        'charttype': charttype,
        'chartdata': chartdata,
    }
    return data


@permission_required('cdr_alert.alarm_report', login_url='/')
@login_required
def alert_report(request):
    """
    To get alarm report for logged in user

    **Attributes**:

        * ``form`` - AlarmReportForm
        * ``template`` - cdr_alert/alarm_report.html
    """
    form = AlarmReportForm(request.user, request.POST or None)
    sort_col_field_list = ['id', 'alarm', 'calculatedvalue', 'status', 'daterun']
    page_data = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')

    alarm_id = 0
    action = 'tabs-1'
    post_var_with_page = 0
    if form.is_valid():
        post_var_with_page = 1
        request.session['session_alarm_id'] = ''
        alarm_id = getvar(request, 'alarm_id', setsession=True)

    if request.GET.get('page') or request.GET.get('sort_by'):
        post_var_with_page = 1
        alarm_id = request.session.get('session_alarm_id')
        form = AlarmReportForm(request.user, initial={'alarm_id': alarm_id})

    if post_var_with_page == 0:
        # unset session var
        request.session['session_alarm_id'] = ''

    kwargs = {}
    if alarm_id and int(alarm_id) != 0:
        kwargs['alarm_id'] = int(alarm_id)
    kwargs['alarm__user'] = request.user

    alarm_report_list = AlarmReport.objects.filter(**kwargs)
    all_alarm_list = alarm_report_list.order_by(page_data['sort_order'])
    alarm_list = all_alarm_list[page_data['start_page']:page_data['end_page']]
    contact_alarm = all_alarm_list.count()

    days_report = last_seven_days_report(request, kwargs)

    data = {
        'form': form,
        'action': action,
        'total_data': days_report['total_data'],
        'start_date': days_report['start_date'],
        'end_date': days_report['end_date'],
        'all_alarm_list': all_alarm_list,
        'rows': alarm_list,
        'total_count': contact_alarm,
        'ALARM_REPORT_COLUMN_NAME': ALARM_REPORT_COLUMN_NAME,
        'col_name_with_order': page_data['col_name_with_order'],
        'charttype': days_report['charttype'],
        'chartdata': days_report['chartdata'],
        'chartcontainer': 'chartcontainer',
        'extra': {
            'x_is_date': True,
            'x_axis_format': '%d %b %y',
            'tag_script_js': False,
            'jquery_on_ready': True,
        },
    }
    return render('cdr_alert/alarm_report.html', data, context_instance=RequestContext(request))


@permission_required('cdr_alert.view_whitelist', login_url='/')
@permission_required('cdr_alert.view_blacklist', login_url='/')
@login_required
def trust_control(request):
    #Blacklist, Whitelist
    blacklist = Blacklist.objects.filter(user=request.user).order_by('id')
    whitelist = Whitelist.objects.filter(user=request.user).order_by('id')

    # blacklist form
    bl_country_form = BWCountryForm(form_type='blacklist')
    bl_prefix_form = BWPrefixForm(form_type='blacklist')

    # whitelist form
    wl_country_form = BWCountryForm(form_type='whitelist')
    wl_prefix_form = BWPrefixForm(form_type='whitelist')

    data = {
        'bl_country_form': bl_country_form,
        'bl_prefix_form': bl_prefix_form,
        'wl_country_form': wl_country_form,
        'wl_prefix_form': wl_prefix_form,
        'blacklist': blacklist,
        'whitelist': whitelist,
    }
    return render('cdr_alert/common_black_white_list.html', data, context_instance=RequestContext(request))
