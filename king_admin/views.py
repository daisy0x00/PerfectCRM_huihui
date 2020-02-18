from django.shortcuts import render,redirect
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage


import importlib
# Create your views here.

from king_admin import king_admin
from king_admin import utils
from king_admin.forms import create_model_form
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    # print(king_admin.enabled_admins)
    # return render(request, "king_admin/table_index.html",{'table_list':'ok'})
    return render(request, "king_admin/table_index.html",{'table_list':king_admin.enabled_admins})

@login_required
def display_table_objs(request,app_name,table_name):
    # print("-->",app_name,table_name)

    # models_module = importlib.import_module('%s.models' %(app_name))
    # model_obj = getattr(models_module,table_name)


    # 获取自定义的admin_class
    admin_class = king_admin.enabled_admins[app_name][table_name]
    # admin_class = king_admin.enabled_admins[crm][userprofile]

    if request.method == 'POST': # action来了
        # with open('1.html','at', encoding="utf-8") as f:
        #     print(request.POST,file=f)
        # 获取提交的数据
        selected_ids = request.POST.get("selected_ids")
        action = request.POST.get("action")
        # 后台判断
        if selected_ids:
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids.split(','))
        else:
            raise KeyError("No object selected.")
        if hasattr(admin_class,action):
            action_func = getattr(admin_class,action)
            # 将action存储在请求体中便于调用
            request._admin_action = action
            return action_func(admin_class,request,selected_objs)




    # 分页处理
    # 1.分页对象参数构建：对象列表，每页显示数量
    # query_set_list = admin_class.model.objects.all()

    # 此处顺序不可乱，搜索是在过滤的基础上建立的
    # 排序又是在过滤和搜索的基础上建立的
    # 延伸===》添加过滤条件
    query_set_list, filter_conditions = utils.table_filter(request, admin_class) # 过滤后的结果
    # 延伸===》添加搜索功能
    query_set_list, search_text = utils.table_search(request, admin_class, query_set_list)
    # 延伸===》添加排序功能
    query_set_list, order_by_text = utils.table_sort(request, admin_class, query_set_list) # 排序后的结果
    # print('order_by_text', order_by_text)
    # 2.分页对象创建
    paginator = Paginator(query_set_list, admin_class.list_per_page)
    # print('admin_class.list_per_page:', admin_class.list_per_page)
    # print(paginator.count)
    # print(paginator.num_pages)
    # print(paginator.page_range)
    # 3.获取前端点击的页面数值
    get_page = request.GET.get('page',1)
    # get_page = int(request.GET.get('page',1))
    # 4.页面异常处理
    try:
        # 直接获取该页内容
        query_set = paginator.page(get_page)
    except PageNotAnInteger:
        # 不是整数值，跳转到首页
        query_set = paginator.page(1)
    except EmptyPage:
        # 超出范围，跳转到最后一页
        query_set = paginator.page(paginator.num_pages)

    return render(request, 'king_admin/table_objs.html',
                  {'admin_class': admin_class,
                   'query_set': query_set,
                   'filter_conditions': filter_conditions,
                   'search_text': search_text,
                   # 'order_by_text':request.GET.get("o",''),
                   'order_by_text':order_by_text,
                   })

    # return render(request,"king_admin/table_objs.html",{"admin_class":admin_class})
    # return render(request,"king_admin/table_objs.html",{"model_obj":model_obj})

@login_required
def table_obj_add(request,app_name,table_name):
    admin_class = king_admin.enabled_admins[app_name][table_name]
    admin_class.is_add_form = True # 标识符
    model_form_class = create_model_form(request, admin_class)

    if request.method == 'POST':
        form_obj = model_form_class(request.POST) # 添加
        if form_obj.is_valid():
            form_obj.save()
            return redirect(request.path.replace("/add/","/"))
    else:
        form_obj = model_form_class()

    return render(request, 'king_admin/table_obj_add.html', {"form_obj": form_obj,
                                                             "admin_class": admin_class})

@login_required
def table_obj_delete(request,app_name,table_name,obj_id):

    admin_class = king_admin.enabled_admins[app_name][table_name]
    obj = admin_class.model.objects.get(id=obj_id)
    if admin_class.readonly_table:
        errors = {"readonly_table":"table is readonly,obj [%s] can not be deleted" % obj}
    else:
        errors = {}
    if request.method == "POST":
        if not admin_class.readonly_table:
            obj.delete()
            return redirect("/king_admin/%s/%s/" %(app_name,table_name))




    return render(request,"king_admin/table_obj_delete.html",{"obj":obj,
                                                              "admin_class": admin_class,
                                                              "app_name": app_name,
                                                              "table_name": table_name,
                                                              "errors":errors})

@login_required
def table_object_edit(request, app_name, table_name, obj_id):
    """
    编辑表中的一条数据
    :param request:
    :param app_name:
    :param table_name:
    :param object_id:
    :return:
    """
    admin_class = king_admin.enabled_admins[app_name][table_name]
    # 创建ModelForm类
    model_form_class = create_model_form(request, admin_class)

    obj = admin_class.model.objects.get(id=obj_id)
    if request.method == 'POST':

        form_obj = model_form_class(request.POST,instance=obj) # 更新
        if form_obj.is_valid():
            form_obj.save()

    else:

        form_obj = model_form_class(instance=obj)


    # return render(request,"king_admin/table_object_edit.html",{"form_obj":form_obj})
    return render(request, 'king_admin/table_object_edit.html',{"form_obj": form_obj,
                                                                "admin_class": admin_class,
                                                                "app_name": app_name,
                                                                "table_name": table_name})

    # # 通过id获取数据库内容
    # object_list = admin_class.model.objects.get(id=obj_id)
    # page = request.GET.get('page')
    # if request.method == 'POST':
    #     # 表单进行验证，更新数据
    #     form_obj = model_form_class(request.POST, instance=object_list) # 更新
    #     if form_obj.is_valid():
    #         form_obj.save()
    #         # 跳转
    #         return redirect('/king_admin/{0}/{1}?page={2}'.format(app_name, table_name, page,))
    #     else:
    #         return render(request, 'king_admin/table_object_edit.html',{"form_obj": form_obj,
    #                                                                     "admin_class": admin_class,
    #                                                                     "app_name": app_name,
    #                                                                     "table_name": table_name})
    # else:
    #     form_obj = model_form_class(instance=object_list)
    #     # with open('1.html', 'wt', encoding='utf-8') as f:
    #     #     print(form_obj, file=f)
    #
    #     return render(request, 'king_admin/table_object_edit.html', {"form_obj": form_obj,
    #                                                              "admin_class": admin_class,
    #                                                              "app_name": app_name,
    #                                                              "table_name": table_name})

@login_required
def password_reset(request, app_name, table_name, obj_id):
    admin_class = king_admin.enabled_admins[app_name][table_name]
    # 创建ModelForm类
    model_form_class = create_model_form(request, admin_class)

    obj = admin_class.model.objects.get(id=obj_id)

    errors = {}
    if request.method == 'POST':
        _password1 = request.POST.get("password1")
        _password2 = request.POST.get("password2")

        if _password1 == _password2:
            if len(_password2) > 5:
                obj.set_password(_password1)
                obj.save()

                return redirect(request.path.rstrip("password/"))
            else:
                errors["password_too_short"] = "must not less than 6 letters"
        else:
            errors["invalid_password"] = "passwords are not the same"


    return render(request,"king_admin/password_reset.html",{'obj':obj,
                                                            'errors':errors})