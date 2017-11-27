##SilverFox(银狐),KBEngine后台管理系统
SilverFox是一个采用[Django](https://www.djangoproject.com/)和基于[Bootstrap](http://v3.bootcss.com/)开发的[Gentelella](https://github.com/puikinsh/gentelella)模板实现的[KBEngine](http://kbengine.org/cn/)服务器后台管理系统.

##安装
安装内容请参考项目根目录里面的安装文档(Installer.md)

##Django的配置
Pycharm打开SilverFox工程,在Pycharm菜单Tools里面选择'Run manage.py task',出现Django的manage.py控制台  


1. 初始化数据库   
控制台输入makemigrations创建相关的迁移文件   
迁移文件创建完毕,输入migrate,在数据库中创建相关的数据库表  
SilverFox默认使用SQLite3作为后台数据库,如果需要更改数据库,请参照Django的相关文档

2. 调试SilverFox   
首先确保KBEngine已经启动  
查看SilverFox.setting.py的MACHINES_ADDRESS配置项的内容是KBEngine启动的服务器IP地址   
在Pycharm菜单Run里面选择'Run SilverFox',等启动完毕,在浏览器输入http://127.0.0.1:8080/就可以调试SilverFox   
用户名和密码在登录界面有说明
