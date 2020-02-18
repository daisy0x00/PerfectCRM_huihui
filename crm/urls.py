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
from crm import views

urlpatterns = [
    url(r'^$', views.index,name="sales_index"),
    url(r'^customer/(\d+)/enrollment/$', views.enrollment,name="enrollment"),
    url(r'^customer/registration/(\d+)/(\w+)/', views.stu_registration,name="stu_registration"),
    url(r'^contract_review/(\d+)/', views.contract_review,name="contract_review"),
    url(r'^payment/(\d+)/', views.payment,name="payment"),
    url(r'^enrollment_rejection/(\d+)/', views.enrollment_rejection,name="enrollment_rejection"),
    url(r'customers/', views.customer_list,name="customer_list"),

]
