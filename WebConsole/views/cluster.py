#!/usr/bin/env python  
# -*- coding: utf-8 -*- 
# Jacky<jackylvm@foxmail.com>
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt

from Common import Machines, Define
from Common.MachinesMgr import machinesmgr
from WebConsole.models import ServerLayout


@login_required
def show(request):
    """"""
    tpl = get_template("manage/cluster.html")
    lst = request.session["kbe_res_path"].split(";")
    dic = {
        "sys_user": request.session["sys_user"],
        "sys_uid": request.session["sys_uid"],
        "kbe_root": request.session["kbe_root"],
        "kbe_res_path": "\n".join(lst),
        "kbe_bin_path": request.session["kbe_bin_path"],
    }
    return HttpResponse(tpl.render(dic, request))


@login_required
@csrf_exempt
def query_machines(request):
    """"""
    servers = machinesmgr.queryMachines()
    lst = []
    for server in servers:
        intaddr = server.intaddr
        lst.append(['{}'.format(intaddr),
                    server.uid,
                    '{:.2f}'.format(server.cpu),
                    '{:.2f}%'.format(server.mem),
                    '{:.2f}'.format(server.extradata2 / 100),
                    '{:.2f}MB'.format(server.usedmem / 1048576),
                    '{:.0f}MB/{:.0f}MB'.format(server.extradata1 / 1048576, server.extradata / 1048576)
                    ])
    datas = {"success": True, "datas": lst}
    return JsonResponse(datas)


@login_required
@csrf_exempt
def query_servers(request):
    """"""
    interfacesGroups = machinesmgr.queryAllInterfaces(0, request.session["sys_user"])
    targetIP = request.POST.get("target", None)

    lst = []
    for mID, comps in interfacesGroups.items():
        if len(comps) > 1 and comps[0].intaddr == targetIP:
            lst = comps[1:]
            break

    ll = []
    for comp in lst:
        ll.append([comp.intaddr,
                   comp.fullname,
                   comp.pid,
                   comp.componentType,
                   comp.componentID,
                   comp.globalOrderID,
                   comp.genuuid_sections,
                   '{:.2f}%'.format(comp.cpu),
                   '{:.2f}%'.format(comp.mem),
                   '{:.2f}MB'.format(comp.usedmem / 1048576),
                   comp.entities,
                   comp.proxies,
                   comp.clients,
                   '<div class="btn-group" role="group" aria-label="...">'
                   '<button class="btn btn-warning btn-xs" type="button" onclick="onStopServer({0},{1},\'{2}\')">STOP</button>'
                   '<button class="btn btn-danger btn-xs" type="button" onclick="onKillServer({0},{1},\'{2}\')">KILL</button>'
                   '</div>'.format(comp.componentType, comp.componentID, comp.fullname),
                   ])
    datas = {"success": True, "datas": ll}
    return JsonResponse(datas)


@login_required
@csrf_exempt
def stop_server(request):
    """"""
    compType = request.POST.get("type", None)
    compID = request.POST.get("id", None)
    if not compType or not compID:
        datas = {"success": False, "datas": []}
        return JsonResponse(datas)
    try:
        compType = int(compType)
        compID = int(compID)
    except Exception as ex:
        print(ex)
        datas = {"success": False, "datas": []}
        return JsonResponse(datas)

    components = Machines.Machines(request.session["sys_uid"], request.session["sys_user"])
    components.stopServer(compType, compID, trycount=0)

    datas = {"success": True, "datas": []}
    return JsonResponse(datas)


@login_required
@csrf_exempt
def kill_server(request):
    """"""
    compType = request.POST.get("type", None)
    compID = request.POST.get("id", None)
    if not compType or not compID:
        datas = {"success": False, "datas": []}
        return JsonResponse(datas)
    try:
        compType = int(compType)
        compID = int(compID)
    except Exception as ex:
        print(ex)
        datas = {"success": False, "datas": []}
        return JsonResponse(datas)

    components = Machines.Machines(request.session["sys_uid"], request.session["sys_user"])
    components.killServer(compType, compID, trycount=0)

    datas = {"success": True, "datas": []}
    return JsonResponse(datas)


COMPS_FOR_SHUTDOWN = [
    Define.BOTS_TYPE,
    Define.LOGINAPP_TYPE,
    Define.CELLAPP_TYPE,
    Define.BASEAPP_TYPE,
    Define.CELLAPPMGR_TYPE,
    Define.BASEAPPMGR_TYPE,
    Define.DBMGR_TYPE,
    Define.INTERFACES_TYPE,
    Define.LOGGER_TYPE,
]


@login_required
@csrf_exempt
def stop_all_servers(request):
    """"""
    uid = request.POST["uid"]
    interfacesGroups = machinesmgr.queryAllInterfaces(int(uid), request.session["sys_user"])
    dic = {}
    for ctid in COMPS_FOR_SHUTDOWN:
        key = Define.COMPONENT_NAME[ctid]
        dic[key] = 0
    for mid, comps in interfacesGroups.items():
        if len(comps) <= 1:
            continue
        for comp in comps:
            if Define.MACHINE_TYPE == comp.componentType:
                continue
            key = Define.COMPONENT_NAME[comp.componentType]
            if key in dic.keys():
                dic[key] += 1
            else:
                dic[key] = 1
    keys = list(dic.keys())
    keys.sort()
    lst = [[key, dic[key]] for key in keys]

    components = Machines.Machines(int(uid), request.session["sys_user"])
    for ctid in COMPS_FOR_SHUTDOWN:
        components.stopServer(ctid, trycount=0)

    datas = {"success": True, "datas": lst}
    return JsonResponse(datas)


@login_required
@csrf_exempt
def query_stop_servers_status(request):
    """"""
    uid = request.POST["uid"]
    interfacesGroups = machinesmgr.queryAllInterfaces(int(uid), request.session["sys_user"])

    dic = {}
    for ctid in COMPS_FOR_SHUTDOWN:
        key = Define.COMPONENT_NAME[ctid]
        dic[key] = 0

    finished = True
    for mid, comps in interfacesGroups.items():
        if len(comps) <= 1:
            continue
        for comp in comps:
            if Define.MACHINE_TYPE == comp.componentType:
                continue

            finished = False
            key = Define.COMPONENT_NAME[comp.componentType]
            if key in dic.keys():
                dic[key] += 1
            else:
                dic[key] = 1
    keys = list(dic.keys())
    keys.sort()
    lst = [[key, dic[key]] for key in keys]
    datas = {"success": True, "datas": lst, "finish": finished}
    return JsonResponse(datas)


@login_required
@csrf_exempt
def run_new_server(request):
    """"""
    try:
        svrtype = int(request.POST["type"])
        ip = request.POST["ip"].strip()
        count = int(request.POST["count"])
    except Exception as ex:
        print(ex)
        datas = {"success": False, "datas": [], "error": "POST参数错误!"}
        return JsonResponse(datas)

    if (svrtype not in Define.VALID_COMPONENT_TYPE_FOR_RUN) or (not machinesmgr.hasMachine(ip)) or (count <= 0):
        print(svrtype, ip, count)
        datas = {"success": False, "datas": [], "error": "POST参数错误!"}
        return JsonResponse(datas)

    kbe_root = request.session["kbe_root"]
    kbe_res_path = request.session["kbe_res_path"]
    kbe_bin_path = request.session["kbe_bin_path"]

    components = Machines.Machines(request.session["sys_uid"], request.session["sys_user"])
    for i in range(count):
        cid = machinesmgr.makeCID(svrtype)
        gus = machinesmgr.makeGUS(svrtype)
        print("cid gus", cid, gus)
        components.startServer(svrtype, cid, gus, ip, kbe_root, kbe_res_path, kbe_bin_path)

    datas = {"success": True, "datas": []}
    return JsonResponse(datas)


VALID_CT = set([
    Define.LOGGER_TYPE,
    Define.INTERFACES_TYPE,
    Define.DBMGR_TYPE,
    Define.BASEAPPMGR_TYPE,
    Define.CELLAPPMGR_TYPE,
    Define.CELLAPP_TYPE,
    Define.BASEAPP_TYPE,
    Define.LOGINAPP_TYPE,
])


@login_required
@csrf_exempt
def save_config(request):
    """"""
    try:
        saveTime = request.POST["time"]
        name = request.POST["name"].strip()
    except Exception as ex:
        print(ex)
        datas = {"success": False, "datas": [], "error": "POST参数错误!"}
        return JsonResponse(datas)
    print(saveTime, type(saveTime))
    print(name, type(name))

    interfaces_groups = machinesmgr.queryAllInterfaces(request.session["sys_uid"], request.session["sys_user"])

    conf = {}

    for machineID, infos in interfaces_groups.items():
        for info in infos:
            if info.componentType not in VALID_CT:
                continue
            compnentName = Define.COMPONENT_NAME[info.componentType]
            if compnentName not in conf:
                conf[compnentName] = []
            d = {"ip": info.intaddr, "cid": info.componentID, "gus": info.genuuid_sections}
            conf[compnentName].append(d)

    if len(conf) == 0:
        datas = {"success": False, "datas": [], "error": "POST参数错误!"}
        return JsonResponse(datas)

    try:
        m = ServerLayout.objects.get(name=name)
    except Exception as ex:
        m = ServerLayout()

    m.name = name
    m.sys_user = request.session["sys_user"]
    m.config = json.dumps(conf)
    m.save()

    datas = {"success": True, "datas": []}
    return JsonResponse(datas)


@login_required
@csrf_exempt
def query_run_configs(request):
    """"""
    qs = ServerLayout.objects.all()
    datas = []
    for q in qs:
        d = {}
        layoutData = json.loads(q.config)
        for ct in VALID_CT:
            compnentName = Define.COMPONENT_NAME[ct]
            if compnentName not in layoutData:
                d[ct] = 0
            else:
                d[ct] = len(layoutData[compnentName])
        opt = '<div class="btn-group" role="group" aria-label="...">' \
              '<button class="btn btn-danger" type="button" onclick="onDeleteConfig({0},\'{1}\')">删除</button>' \
              '<button class="btn btn-primary" type="button" onclick="onLoadConfig({0},\'{1}\')">加载</button>' \
              '</div>'.format(q.id, q.name)
        datas.append([q.name, q.sys_user, d[Define.CELLAPP_TYPE], d[Define.BASEAPP_TYPE], d[Define.CELLAPPMGR_TYPE],
                      d[Define.BASEAPPMGR_TYPE], d[Define.LOGINAPP_TYPE], d[Define.DBMGR_TYPE],
                      d[Define.INTERFACES_TYPE], d[Define.LOGGER_TYPE], opt])
    datas = {"success": True, "datas": datas}
    return JsonResponse(datas)


@login_required
@csrf_exempt
def delete_config(request):
    """"""
    try:
        id = int(request.POST["id"])
    except Exception as ex:
        print(ex)
        id = 0

    if not id:
        datas = {"success": False, "datas": []}
        return JsonResponse(datas)

    ServerLayout.objects.filter(id=id).delete()

    datas = {"success": True, "datas": []}
    return JsonResponse(datas)


@login_required
@csrf_exempt
def load_config(request):
    """"""
    kbe_root = request.session["kbe_root"]
    kbe_res_path = request.session["kbe_res_path"]
    kbe_bin_path = request.session["kbe_bin_path"]
    try:
        id = int(request.POST["id"])
    except Exception as ex:
        print(ex)
        id = 0
    if not id:
        datas = {"success": False, "error": "参数错误!"}
        return JsonResponse(datas)

    components = Machines.Machines(request.session["sys_uid"], request.session["sys_user"])
    interfaces_groups = machinesmgr.queryAllInterfaces(request.session["sys_uid"], request.session["sys_user"])

    for mID, comps in interfaces_groups.items():
        if len(comps) > 1:
            datas = {"success": False, "error": "服务器正在运行,不允许加载!"}
            return JsonResponse(datas)

    # 计数器
    t2c = [0, ] * len(Define.COMPONENT_NAME)
    components_ct = [0, ] * len(Define.COMPONENT_NAME)
    components_cid = [0, ] * len(Define.COMPONENT_NAME)
    components_gus = [0, ] * len(Define.COMPONENT_NAME)
    ly = ServerLayout.objects.get(pk=id)
    layoutData = json.loads(ly.config)
    lst = [
        Define.LOGGER_TYPE,
        Define.INTERFACES_TYPE,
        Define.DBMGR_TYPE,
        Define.BASEAPPMGR_TYPE,
        Define.CELLAPPMGR_TYPE,
        Define.CELLAPP_TYPE,
        Define.BASEAPP_TYPE,
        Define.LOGINAPP_TYPE,
    ]
    for ct in lst:
        compnentName = Define.COMPONENT_NAME[ct]
        components_ct[ct] = ct
        for comp in layoutData.get(compnentName, []):
            cid = comp["cid"]
            if cid <= 0:
                cid = machinesmgr.makeCID(ct)
            components_cid[ct] = cid

            gus = comp["gus"]
            if gus <= 0:
                gus = machinesmgr.makeGUS(ct)
            components_gus[ct] = gus
            t2c[ct] += 1
            components.startServer(ct, cid, gus, comp["ip"], kbe_root, kbe_res_path, kbe_bin_path, 0)

    datas = {"success": True, "datas": []}
    return JsonResponse(datas)
