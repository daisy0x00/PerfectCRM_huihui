"""PerfectCRMv1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from king_admin import views

urlpatterns = [
    url(r'^$', views.index,name="table_index"), # name是对应数据库中的映射关系
    # 域名/后台名称/应用名称/表名/
    url(r'^(\w+)/(\w+)/$', views.display_table_objs,name="table_objs"), # 添加该数据，参数分别表示应用名和表名，name同样表示映射关系的引用
    url(r'^(\w+)/(\w+)/(\d+)/edit/$', views.table_object_edit, name="table_object_edit"),
    url(r'^(\w+)/(\w+)/(\d+)/edit/password/$', views.password_reset, name="password_reset"),
    url(r'^(\w+)/(\w+)/(\d+)/delete/$', views.table_obj_delete, name="obj_delete"),
    url(r'^(\w+)/(\w+)/add/$', views.table_obj_add, name="table_obj_add"),
]
