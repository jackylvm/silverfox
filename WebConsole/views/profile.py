#!/usr/bin/env python  
# -*- coding: utf-8 -*- 
# Jacky<jackylvm@foxmail.com>
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template

from Common import Define
from Common.MachinesMgr import machinesmgr
from WebConsole.common.telnet_console import ProfileConsole
from dwebsocket import accept_websocket


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
                wsurl = "ws://{}/wc/profile/query/profile?host={}&port={}".format(webaddr, comp.intaddr,
                                                                                  comp.consolePort)
                wsurl1 = "{}&cmd=pytickprofile".format(wsurl)
                wsurl2 = "{}&cmd=cprofile".format(wsurl)
                wsurl3 = "{}&cmd=pyprofile".format(wsurl)
                wsurl4 = "{}&cmd=eventprofile".format(wsurl)
                wsurl5 = "{}&cmd=networkprofile".format(wsurl)

                pytick.append([json.dumps(
                    {"wsurl": wsurl1, "cmd": "pytickprofile", "ip": comp.intaddr, "port": comp.consolePort,
                     "title": "TickProfile"}),
                               comp.fullname])
                cp.append(
                    [json.dumps({"wsurl": wsurl2, "cmd": "cprofile", "ip": comp.intaddr, "port": comp.consolePort,
                                 "title": "CPProfile"}),
                     comp.fullname])
                py.append(
                    [json.dumps({"wsurl": wsurl3, "cmd": "pyprofile", "ip": comp.intaddr, "port": comp.consolePort,
                                 "title": "PYProfile"}),
                     comp.fullname])
                event.append([json.dumps(
                    {"wsurl": wsurl4, "cmd": "eventprofile", "ip": comp.intaddr, "port": comp.consolePort,
                     "title": "EventProfile"}),
                    comp.fullname])
                network.append([json.dumps(
                    {"wsurl": wsurl5, "cmd": "networkprofile", "ip": comp.intaddr, "port": comp.consolePort,
                     "title": "NetworkProfile"}),
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
@accept_websocket
def query_profile(request):
    """"""
    try:
        cmd = request.GET["cmd"]
        host = request.GET["host"]
        port = int(request.GET["port"])
        sec = request.GET["sec"]
    except Exception as ex:
        print(ex)
        datas = {"success": False, "datas": []}
        return JsonResponse(datas)
    print("query_profile>>>", host, port, cmd, sec)
    console = ProfileConsole(request.websocket, host, port, cmd, sec)
    console.run()
    datas = {"success": True, "datas": []}
    return JsonResponse(datas)
