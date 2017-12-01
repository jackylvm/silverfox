"""SilverFox URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url

from WebConsole.views import views, users, cluster, log, status, profile, console, watcher, space

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login', views.login),
    url(r'^dologin', views.dologin),
    url(r'^logout', views.logout),
    url(r'^index', views.index),

    url(r'^user/manage', users.manage),
    url(r'^user/query/all', users.query_all),

    url(r'^cluster/show', cluster.show),
    url(r'^cluster/query/machines', cluster.query_machines),
    url(r'^cluster/query/servers', cluster.query_servers),
    url(r'^cluster/stop/server', cluster.stop_server),
    url(r'^cluster/kill/server', cluster.kill_server),
    url(r'^cluster/stop/all/servers', cluster.stop_all_servers),
    url(r'^cluster/query/stop/servers/status', cluster.query_stop_servers_status),
    url(r'^cluster/run/new/server', cluster.run_new_server),
    url(r'^cluster/save/config', cluster.save_config),
    url(r'^cluster/query/run/configs', cluster.query_run_configs),
    url(r'^cluster/delete/config', cluster.delete_config),
    url(r'^cluster/load/config', cluster.load_config),

    url(r'^log/show', log.show),
    url(r'^ws/log/query/logs', log.query_logs),

    url(r'^status/show', status.show),
    url(r'^wc/status/query/status', status.query_status),

    url(r'^profile/show', profile.show),
    url(r'^wc/profile/query/profile', profile.query_profile),

    url(r'^console/show', console.show),
    url(r'^wc/console/open', console.console_open),

    url(r'^watcher/show', watcher.show),
    url(r'^wc/watcher/open', watcher.watcher_open),

    url(r'^space/show', space.show),
]
