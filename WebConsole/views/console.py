#!/usr/bin/env python  
# -*- coding: utf-8 -*- 
# Jacky<jackylvm@foxmail.com>
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template

import Define
from MachinesMgr import machinesmgr
from WebConsole.common.telnet_console import TelnetConsole
from dwebsocket import accept_websocket

VALID_CT = {
    Define.DBMGR_TYPE,
    Define.LOGINAPP_TYPE,
    Define.CELLAPP_TYPE,
    Define.BASEAPP_TYPE,
    Define.INTERFACES_TYPE,
    Define.LOGGER_TYPE,
}


@login_required
def show(request):
    """"""
    tpl = get_template("manage/console.html")
    webaddr = request.META["HTTP_HOST"]

    interfaces_groups = machinesmgr.queryAllInterfaces(request.session["sys_uid"], request.session["sys_user"])

    # [(machine, [components, ...]), ...]
    kbeComps = []
    for mID, comps in interfaces_groups.items():
        for comp in comps:
            if comp.componentType in VALID_CT:
                wsurl = "ws://{}/wc/console/open?host={}&port={}".format(webaddr, comp.intaddr, comp.consolePort)
                compname = Define.COMPONENT_NAME[comp.componentType]
                value = {"wsurl": wsurl, "name": compname}
                kbeComps.append([json.dumps(value), comp.fullname])

    return HttpResponse(tpl.render({"comps": kbeComps}, request))


@login_required
@accept_websocket
def console_open(request):
    """"""
    try:
        host = request.GET["host"]
        port = int(request.GET["port"])
    except Exception as ex:
        print(ex)
        datas = {"success": False, "datas": []}
        return JsonResponse(datas)
    console = TelnetConsole(request.websocket, host, port)
    console.run()
    datas = {"success": True, "datas": []}
    return JsonResponse(datas)
