#!/usr/bin/env python  
# -*- coding: utf-8 -*- 
# Jacky<jackylvm@foxmail.com>
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template

import Define
from Common import SpaceViews
from MachinesMgr import machinesmgr
from dwebsocket import accept_websocket

VALID_CT = {
    Define.CELLAPPMGR_TYPE,
    Define.CELLAPP_TYPE,
}


@login_required
def show(request):
    """"""
    tpl = get_template("manage/space.html")
    webaddr = request.META["HTTP_HOST"]

    interfaces_groups = machinesmgr.queryAllInterfaces(request.session["sys_uid"], request.session["sys_user"])

    # [(machine, [components, ...]), ...]
    cellMgrWSUrl = ""
    cells = []
    for mID, comps in interfaces_groups.items():
        for comp in comps:
            if comp.componentType in VALID_CT:
                if Define.CELLAPPMGR_TYPE == comp.componentType:
                    cellMgrWSUrl = "ws://{}/wc/space/mgr/open?cp={}&host={}&port={}".format(webaddr, comp.componentType,
                                                                                            comp.intaddr,
                                                                                            comp.intport)
                else:
                    wsurl = "ws://{}/wc/space/cell/open?cp={}&host={}&port={}".format(webaddr, comp.componentType,
                                                                                      comp.intaddr,
                                                                                      comp.intport)
                    cell = [comp.componentID, wsurl]
                    cells.append(cell)
    print(json.dumps(cells))
    return HttpResponse(tpl.render({"cells": cells, "cellMgrWSUrl": cellMgrWSUrl}, request))


@login_required
@accept_websocket
def mgr_open(request):
    """"""
    try:
        type = int(request.GET["cp"])
        host = request.GET["host"]
        port = int(request.GET["port"])
    except Exception as ex:
        print(ex)
        datas = {"success": False, "datas": []}
        return JsonResponse(datas)
    space = SpaceDate(request.websocket, type, host, port)
    space.do()
    datas = {"success": True, "datas": []}
    return JsonResponse(datas)


@login_required
@accept_websocket
def cell_open(request):
    """"""
    try:
        type = int(request.GET["cp"])
        host = request.GET["host"]
        port = int(request.GET["port"])
        spaceID = int(request.GET["spaceID"])
    except Exception as ex:
        print(ex)
        datas = {"success": False, "datas": []}
        return JsonResponse(datas)
    space = CellSpace(request.websocket, type, host, port, spaceID)
    space.do()
    datas = {"success": True, "datas": []}
    return JsonResponse(datas)


class SpaceDate(object):
    """"""

    def __init__(self, wInst, cp, host, port):
        """"""
        self.wsInst = wInst
        self.cp = cp
        self.port = port
        self.host = host
        self.spaceViews = None

    def do(self):
        """"""
        self.spaceViews = SpaceViews.SpaceViewer(self.cp)
        self.spaceViews.connect(self.host, self.port)
        self.test = ""
        while True:
            self.spaceViews.requireQuerySpaceViewer()
            self.spaceViews.processOne(0.1)
            if self.spaceViews.SpaceViewerData != self.test:
                data = json.dumps(self.spaceViews.SpaceViewerData)
                self.wsInst.send(data.encode())
                self.test = self.spaceViews.SpaceViewerData

            if self.wsInst.has_messages():
                data = self.wsInst.read()
                if -1 != data.find(b'stop'):
                    self.close()
                    if self.spaceViews:
                        self.spaceViews.clearSpaceViewerData()
                        self.spaceViews.close()
                        break
            self.spaceViews.clearSpaceViewerData()

    def close(self):
        """"""
        if self.wsInst:
            self.wsInst.close()


class CellSpace(object):
    def __init__(self, wInst, cp, host, port, spaceID):
        self.wsInst = wInst
        self.cp = cp
        self.port = port
        self.host = host
        self.spaceID = spaceID
        self.test = ""
        self.cellSpaceViewer = None

    def do(self):
        self.cellSpaceViewer = SpaceViews.CellViewer(self.cp, self.spaceID)
        self.cellSpaceViewer.connect(self.host, self.port)
        while True:
            self.cellSpaceViewer.requireQueryCellViewer()
            self.cellSpaceViewer.processOne(0.1)
            if self.cellSpaceViewer.CellViewerData != self.test:
                data = json.dumps(self.cellSpaceViewer.CellViewerData)
                self.wsInst.send(data.encode())
                self.test = self.cellSpaceViewer.CellViewerData

            if self.wsInst.has_messages():
                data = self.wsInst.read()
                if -1 != data.find(b'stop'):
                    self.close()
                    if self.cellSpaceViewer:
                        self.cellSpaceViewer.clearCellViewerData()
                        self.cellSpaceViewer.close()
                        break

            self.cellSpaceViewer.clearCellViewerData()

    def close(self):
        if self.wsInst:
            self.wsInst.close()
        self.wsInst = None
