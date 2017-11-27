#!/usr/bin/env python  
# -*- coding: utf-8 -*- 
# Jacky<jackylvm@foxmail.com>
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template

import Define
from MachinesMgr import machinesmgr

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
    kbeComps = []
    for mID, comps in interfaces_groups.items():
        for comp in comps:
            if comp.componentType in VALID_CT:
                wsurl = "ws://{}/wc/space/open?host={}&port={}".format(webaddr, comp.intaddr, comp.intport)
                compname = Define.COMPONENT_NAME[comp.componentType]
                value = {"wsurl": wsurl, "name": compname}
                kbeComps.append([json.dumps(value), comp.fullname])

    return HttpResponse(tpl.render({"comps": kbeComps}, request))
