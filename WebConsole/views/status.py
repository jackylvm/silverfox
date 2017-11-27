#!/usr/bin/env python  
# -*- coding: utf-8 -*- 
# Jacky<jackylvm@foxmail.com>
import json
import time
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template

import Component_Status
import Define
from MachinesMgr import machinesmgr
from plugins.dwebsocket import accept_websocket

VALID_CT = [
    Define.BASEAPPMGR_TYPE,
    Define.CELLAPPMGR_TYPE,
]


@login_required
def show(request):
    """"""
    tpl = get_template("manage/status.html")
    webaddr = request.META["HTTP_HOST"]

    interfaces_groups = machinesmgr.queryAllInterfaces(request.session["sys_uid"], request.session["sys_user"])

    # [(machine, [components, ...]), ...]
    kbeComps = []
    compsCount = {}
    for mID, comps in interfaces_groups.items():
        for comp in comps:
            if comp.componentType in VALID_CT:
                wsurl = "ws://{}/wc/status/query/status?cp={}&host={}&port={}".format(webaddr, comp.componentType,
                                                                                      comp.intaddr, comp.intport)
                compname = Define.COMPONENT_NAME[comp.componentType]
                value = {"wsurl": wsurl, "name": compname}
                kbeComps.append([json.dumps(value), comp.fullname])
                if compname in compsCount.keys():
                    compsCount[compname] += 1
                else:
                    compsCount[compname] = 1

    return HttpResponse(tpl.render({"comps": kbeComps, "counts": compsCount}, request))


@login_required
@accept_websocket
def query_status(request):
    """"""
    try:
        cp = int(request.GET["cp"])
        host = request.GET["host"]
        port = int(request.GET["port"])
    except Exception as ex:
        print(ex)
        datas = {"success": False, "datas": []}
        return JsonResponse(datas)
    compStatus = CompStatusData(request.websocket, cp, host, port)
    compStatus.do()
    datas = {"success": True, "datas": []}
    return JsonResponse(datas)


class CompStatusData():
    """"""

    def __init__(self, wsInst, cp, host, port):
        """"""
        self._wsInst = wsInst
        self._cp = cp
        self._host = host
        self._port = port
        self._compStatus = Component_Status.ComponentStatus(cp)

    def do(self):
        """"""
        self._compStatus.connect(self._host, self._port)
        self._compStatus.requireQueryCS()
        while True:
            if self._wsInst.has_messages():
                data = self._wsInst.read()
                if data and -1 != data.find(b'stop'):
                    self.close()
                    return False

            self._compStatus.processOne()
            time.sleep(0.5)
            sendData = {"componentID": self._compStatus.CSData["componentID"],
                        "load": self._compStatus.CSData["load"],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            self._wsInst.send(bytes(json.dumps(sendData), encoding="utf8"))
            self._compStatus.clearCSData()
            time.sleep(4.5)
            self._compStatus.requireQueryCS()

    def close(self):
        """"""
        if self._compStatus:
            self._compStatus.clearCSData()
            self._compStatus.close()
            self._compStatus = None

        if self._wsInst:
            self._wsInst.close()
        self._wsInst = None
