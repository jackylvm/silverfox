#!/usr/bin/env python  
# -*- coding: utf-8 -*- 
# Jacky<jackylvm@foxmail.com>
import json
import time

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template

import Define
from Common import Watcher
from MachinesMgr import machinesmgr
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
    tpl = get_template("manage/watcher.html")
    webaddr = request.META["HTTP_HOST"]

    interfaces_groups = machinesmgr.queryAllInterfaces(request.session["sys_uid"], request.session["sys_user"])

    # [(machine, [components, ...]), ...]
    kbeComps = []
    for mID, comps in interfaces_groups.items():
        for comp in comps:
            if comp.componentType in VALID_CT:
                wsurl = "ws://{}/wc/watcher/open?cp={}&host={}&port={}".format(webaddr, comp.componentType,
                                                                               comp.intaddr, comp.intport)
                compname = Define.COMPONENT_NAME[comp.componentType]
                value = {"wsurl": wsurl, "name": compname}
                kbeComps.append([json.dumps(value), comp.fullname])

    return HttpResponse(tpl.render({"comps": kbeComps}, request))


@login_required
@accept_websocket
def watcher_open(request):
    """"""
    try:
        type = int(request.GET["cp"])
        host = request.GET["host"]
        port = int(request.GET["port"])
        key = request.GET["key"]
    except Exception as ex:
        print(ex)
        datas = {"success": False, "datas": []}
        return JsonResponse(datas)
    console = WatcherData(request.websocket, type, host, port, key)
    console.do()
    datas = {"success": True, "datas": []}
    return JsonResponse(datas)


class WatcherData(object):
    def __init__(self, wInst, cp, host, port, key):
        self.wsInst = wInst
        self.cp = cp
        self.port = port
        self.host = host
        self.key = key
        self.watcher = Watcher.Watcher(cp)

    def do(self):
        self.watcher.connect(self.host, self.port)
        self.watcher.requireQueryWatcher(self.key)
        while True:
            if not self.watcher.watchData:
                self.watcher.processOne()
                if self.key == "root/network/messages":
                    time.sleep(1)
                else:
                    time.sleep(0.5)
            else:
                print(self.watcher.watchData)
                self.wsInst.send(str.encode(str(self.watcher.watchData)))
                if self.wsInst.has_messages():
                    data = self.wsInst.read()
                    if -1 != data.find(b'stop'):
                        self.close()
                        if self.watcher:
                            self.watcher.close()
                            break

                self.watcher.clearWatchData()
                self.watcher.requireQueryWatcher(self.key)

    def close(self):
        if self.wsInst:
            self.wsInst.close()
            self.wsInst = None
