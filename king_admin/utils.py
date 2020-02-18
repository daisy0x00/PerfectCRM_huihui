#coding:utf-8
from django.db.models import Q

#------------过滤功能---------------
def table_filter(request, admin_class):
    """
    条件过滤，并构造过滤后的数据结构
    :param request:
    :param admin_class:
    :return:
    """
    filter_conditions = {}
    # 保留关键字，page分页关键字，o排序关键字
    keywords = ['page', '_q', 'o']
    for k,v in request.GET.items():
        if k in keywords:# 保留关键字
            continue
        if v:
            filter_conditions[k] = v

    # print('filter_conditions:',filter_conditions)
    # print("admin_class.model.objects.filter(**filter_conditions)", admin_class.model.objects.filter(**filter_conditions))
    return admin_class.model.objects.filter(**filter_conditions), filter_conditions

#------------------搜索功能--------------------------
def table_search(request,admin_class,object_list):
    """

    :param request: 封装的请求体
    :param admin_class: 自定义类
    :param object_list: 过滤后的数据
    :return:
    """
    # 在请求中通过参数查询结果
    search_text = request.GET.get("_q","")
    # 创建Q查询对象，组合搜索
    q_obj = Q()
    # 设定连接方式
    q_obj.connector = "OR"
    # 遍历搜索选项
    for search_words in admin_class.search_fields:
        q_obj.children.append(("{0}__contains".format(search_words), search_text))
    search_result = object_list.filter(q_obj)
    return search_result, search_text

#-------------------------排序功能-----------------------------
def table_sort(request,admin_class, query_set_list):
    """
    默认情况下，Django中取出来的数据是无序的
    :param request:
    :param admin_class:
    :param query_set_list: 过滤、搜索之后的数据
    :return:
    """
    #-----------------初始化排序设定---------------------------
    # 默认排序条件---降序
    king_admin_ordering = "-{0}".format(admin_class.ordering if admin_class.ordering else "-id")
    # 获取排序后结果
    order_by_init = query_set_list.order_by(king_admin_ordering)



    #------------------排序判断-------------------------------
    # 通过参数获取到结果，默认None，修改为空
    order_by_text = request.GET.get('o', '')
    # 判断是否存在
    if order_by_text:
        # 存在即根据获取字段排反序
        order_result = order_by_init.order_by(order_by_text)
        # 下次获取到的数据排序，要取反结果即： 添加或去除’-‘
        # 判断是否存在’-‘，存在就去掉’-‘
        if order_by_text.startswith('-'):
            order_by_text = order_by_text.strip('-')
        # 没有就加上
        else:
            order_by_text = '-{0}'.format(order_by_text)
     #不存在返回数据
    else:
        order_result = order_by_init
    return order_result, order_by_text