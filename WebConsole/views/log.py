#!/usr/bin/env python  
# -*- coding: utf-8 -*- 
# Jacky<jackylvm@foxmail.com>
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template

from Common import Define
from Common.LoggerWatcher import LoggerWatcher
from Common.MachinesMgr import machinesmgr
from plugins.dwebsocket import accept_websocket


@login_required
def show(request):
    """"""
    VALID_CT = [Define.LOGGER_TYPE]
    interfaces_groups = machinesmgr.queryAllInterfaces(request.session["sys_uid"], request.session["sys_user"])
    kbeComps = []
    for mID, comps in interfaces_groups.items():
        for comp in comps:
            if comp.componentType in VALID_CT:
                kbeComps.append(comp)

    webaddr = request.META["HTTP_HOST"]
    tpl = get_template("manage/log.html")
    try:
        intaddr = kbeComps[0].intaddr
        intport = kbeComps[0].intport
        extaddr = kbeComps[0].extaddr
        extport = kbeComps[0].extport
        uid = request.session["sys_uid"]
    except:
        return HttpResponse(tpl.render({"intaddr": '',
                                        "intport": 0,
                                        "extaddr": '',
                                        "extport": 0,
                                        "uid": 0,
                                        "webaddr": webaddr}, request))

    return HttpResponse(tpl.render({"intaddr": intaddr,
                                    "intport": intport,
                                    "extaddr": extaddr,
                                    "extport": extport,
                                    "uid": uid,
                                    "webaddr": webaddr,
                                    }, request))


@login_required
@accept_websocket
def query_logs(request):
    """"""
    try:
        extaddr = request.GET["extaddr"]
        extport = int(request.GET["extport"])
        uid = int(request.GET["uid"])
    except Exception as ex:
        print(ex)
        datas = {"success": False, "datas": []}
        return JsonResponse(datas)

    compChk = [0 for i in range(14)]
    flag = True
    comp = request.GET.get("baseapp", "0")
    if "1" == comp:
        flag = False
        compChk[Define.BASEAPP_TYPE] = Define.BASEAPP_TYPE
    comp = request.GET.get("cellapp", "0")
    if "1" == comp:
        flag = False
        compChk[Define.CELLAPP_TYPE] = Define.CELLAPP_TYPE
    comp = request.GET.get("baseappmgr", "0")
    if "1" == comp:
        flag = False
        compChk[Define.BASEAPPMGR_TYPE] = Define.BASEAPPMGR_TYPE
    comp = request.GET.get("cellappmgr", "0")
    if "1" == comp:
        flag = False
        compChk[Define.CELLAPPMGR_TYPE] = Define.CELLAPPMGR_TYPE
    comp = request.GET.get("dbmgr", "0")
    if "1" == comp:
        flag = False
        compChk[Define.DBMGR_TYPE] = Define.DBMGR_TYPE
    comp = request.GET.get("loginapp", "0")
    if "1" == comp:
        flag = False
        compChk[Define.LOGINAPP_TYPE] = Define.LOGINAPP_TYPE
    if flag:
        i = -1
        for x in compChk:
            i = i + 1
            compChk[x] = i

    logtype = int(request.GET.get("logtype", "0"))
    # 自定义搜索
    globalOrder = request.GET.get("global", "0")
    groupOrder = request.GET.get("group", "0")
    if globalOrder == '':
        globalOrder = 0
    if groupOrder == '':
        groupOrder = 0

    globalOrder = int(globalOrder)
    groupOrder = int(groupOrder)
    searchDate = request.GET.get("searchDate", "")
    keystr = request.GET.get("keystr", "")

    console = LogWatch(request.websocket, extaddr, extport, uid, compChk, logtype, globalOrder, groupOrder, searchDate,
                       keystr)
    console.do()

    datas = {"success": True, "datas": []}
    return JsonResponse(datas)


class LogWatch(object):
    """
    日志输出
    """

    def __init__(self, wsInst, extaddr, extport, uid, components_check, logtype, globalOrder, groupOrder, searchDate,
                 keystr):
        self.wsInst = wsInst
        self.extaddr = extaddr
        self.extport = extport
        self.uid = uid
        self.components_check = components_check
        self.logtype = logtype
        self.globalOrder = globalOrder
        self.groupOrder = groupOrder
        self.searchDate = searchDate
        self.keystr = keystr
        self.logger = LoggerWatcher()
        self.previous_log = []

    def do(self):
        """
        """
        self.logger.close()
        self.logger.connect(self.extaddr, self.extport)
        self.logger.registerToLoggerForWeb(self.uid, self.components_check, self.logtype, self.globalOrder,
                                           self.groupOrder, self.searchDate, self.keystr)

        def onReceivedLog(logs):
            """"""
            if self.wsInst.has_messages():
                data = self.wsInst.read()
                if -1 != data.find(b'stop'):
                    self.close()
                    return False

            new_logs = list(set(logs) ^ set(self.previous_log))
            for e in new_logs:
                self.wsInst.send(e)
            self.previous_log = logs
            return True

        self.logger.receiveLog(onReceivedLog, True)

    def close(self):
        """ """
        self.logger.deregisterFromLogger()
        self.logger.close()

        if self.wsInst:
            self.wsInst.close()
        self.wsInst = None

        self.extaddr = ""
        self.extport = 0
