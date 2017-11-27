#!/usr/bin/env python  
# -*- coding: utf-8 -*- 
# Jacky<jackylvm@foxmail.com>
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt

import Define
from MachinesMgr import machinesmgr


@login_required
def show(request):
    """"""
    VALID_CT = {Define.DBMGR_TYPE, Define.LOGINAPP_TYPE, Define.CELLAPP_TYPE, Define.BASEAPP_TYPE,
                Define.INTERFACES_TYPE, Define.LOGGER_TYPE}

    interfacesGroups = machinesmgr.queryAllInterfaces(request.session["sys_uid"], request.session["sys_user"])

    webaddr = request.META["HTTP_HOST"]
    pytick = []
    cp = []
    py = []
    event = []
    network = []
    for mID, comps in interfacesGroups.items():
        for comp in comps:
            if comp.componentType in VALID_CT:
                wsurl = "ws://{}/wc/profile/query?host={}&port={}".format(webaddr, comp.intaddr, comp.consolePort)
                wsurl1 = "{}&cmd=pytickprofile".format(wsurl)
                wsurl2 = "{}&cmd=cprofile".format(wsurl)
                wsurl3 = "{}&cmd=pyprofile".format(wsurl)
                wsurl4 = "{}&cmd=eventprofile".format(wsurl)
                wsurl5 = "{}&cmd=networkprofile".format(wsurl)

                pytick.append([json.dumps(
                    {"wsurl": wsurl1, "ip": comp.intaddr, "port": comp.consolePort, "title": "TickProfile"}),
                    comp.fullname])
                cp.append(
                    [json.dumps({"wsurl": wsurl2, "ip": comp.intaddr, "port": comp.consolePort, "title": "CPProfile"}),
                     comp.fullname])
                py.append(
                    [json.dumps({"wsurl": wsurl3, "ip": comp.intaddr, "port": comp.consolePort, "title": "PYProfile"}),
                     comp.fullname])
                event.append([json.dumps(
                    {"wsurl": wsurl4, "ip": comp.intaddr, "port": comp.consolePort, "title": "EventProfile"}),
                    comp.fullname])
                network.append([json.dumps(
                    {"wsurl": wsurl5, "ip": comp.intaddr, "port": comp.consolePort, "title": "NetworkProfile"}),
                    comp.fullname])

    tpl = get_template("manage/profile.html")
    return HttpResponse(tpl.render({
        "pytick": pytick,
        "cp": cp,
        "py": py,
        "event": event,
        "network": network
    }, request))


@login_required
@csrf_exempt
def query_components(request):
    """"""
    VALID_CT = {Define.DBMGR_TYPE, Define.LOGINAPP_TYPE, Define.CELLAPP_TYPE, Define.BASEAPP_TYPE,
                Define.INTERFACES_TYPE, Define.LOGGER_TYPE}

    interfacesGroups = machinesmgr.queryAllInterfaces(request.session["sys_uid"], request.session["sys_user"])

    lst = []
    for mID, comps in interfacesGroups.items():
        for comp in comps:
            if comp.componentType in VALID_CT:
                intaddr = comp.intaddr
                consolePort = comp.consolePort
                title = "with {} on {}:{}".format(comp.fullname, intaddr, consolePort)
                opt = '<div class="btn-group" role="group" aria-label="...">' \
                      '<button class="btn btn-primary" type="button" onclick="onTickProfile(\'{0}\',{1},\'TickProfile {2}\',\'pytickprofile\',\'TickProfile\')">TickProfile</button>' \
                      '<button class="btn btn-success" type="button" onclick="onCPProfile(\'{0}\',{1},\'CPProfile {2}\',\'cprofile\',\'CPProfile\')">CPProfile</button>' \
                      '<button class="btn btn-primary" type="button" onclick="onPYProfile(\'{0}\',{1},\'PYProfile {2}\',\'pyprofile\',\'PYProfile\')">PYProfile</button>' \
                      '<button class="btn btn-success" type="button" onclick="onEventProfile(\'{0}\',{1},\'EventProfile {2}\',\'eventprofile\',\'EventProfile\')">EventProfile</button>' \
                      '<button class="btn btn-primary" type="button" onclick="onNetworkProfile(\'{0}\',{1},\'NetworkProfile {2}\',\'networkprofile\',\'NetworkProfile\')">NetworkProfile</button>' \
                      '</div>'.format(intaddr, consolePort, title)
                lst.append([comp.intaddr,
                            comp.fullname,
                            comp.componentID,
                            opt])
    datas = {"success": True, "datas": lst}
    return JsonResponse(datas)
