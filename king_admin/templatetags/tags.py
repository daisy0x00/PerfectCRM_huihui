from django import template
from django.core.exceptions import FieldDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime,timedelta


# from king_admin.utils import table_filter

register = template.Library()

# --------------显示表名称-》中文----------------
@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name_plural

# 获取到表的所有数据
@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()

#------------创建表格行数据----------------
@register.simple_tag
def build_table_row(request, obj,admin_class):
    # 创建标签元素--空，None不行
    row_ele = ""

    # 遍历要显示的models字段
    for number, column in enumerate(admin_class.list_display):
        # 获取显示字段对应的字段对象类型
        # field_obj = obj._meta.get_field(column)
        try:
            field_obj = admin_class.model._meta.get_field(column)
            # 获取数据
            # 判断choice
            # 如果是choice字段，则通过反射取它的名字
            if field_obj.choices:
                # 通过反射获取对象里面的值，并执行该方法get_字段_display()获取choices里面的数值
                column_data = getattr(obj,"get_{0}_display".format(column))()
            else:
                column_data = getattr(obj,column)

            # 时间格式转换
            if type(column_data).__name__ == 'datetime':
                column_data = column_data.strftime('%Y-%m-%d %H-%M-%S')

            # 添加编辑页面入口,如果是第一列可以点击进去编辑数据
            if number == 0: # add a tag,加上a标签，可以跳转到修改页
                column_data = "<a href='{request_path}{obj_id}/edit/'>{data}</a>".format(request_path=request.path,
                                                                                      obj_id=obj.id,
                                                                                      data=column_data)
        except FieldDoesNotExist as e:
            if hasattr(admin_class,column):
                column_func = getattr(admin_class,column)
                admin_class.instance = obj
                admin_class.request = request
                column_data = column_func()
        # 标签元素的拼接
        row_ele += "<td>%s</td>" %column_data


    return mark_safe(row_ele)
    # return row_ele

@register.simple_tag
def render_page_ele(loop_counter, query_sets, filter_conditions):
    filters = ''
    for k,v in filter_conditions.items():
        filters += "&%s=%s" %(k, v)
    if abs(query_sets.number - loop_counter) <= 1:
        ele_class =""
        if query_sets.number == loop_counter:
            ele_class = "active"
        ele = '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' %(ele_class,loop_counter, filters, loop_counter)

        return mark_safe(ele)

#------------分页处理------------
#------------分页优化------------
@register.simple_tag
def create_page_element(query_set, filter_conditions,search_text, order_by_text):
    """
    返回整个分页元素
    :param query_set:
    :return:
    """
    page_btns = ''
    filters = ''
    # 过滤条件
    for k, v in filter_conditions.items():
        filters += '&{0}={1}'.format(k, v)

    added_dot_ele = False #  标志符， 标志是否加了...

    for page_num in query_set.paginator.page_range:
        # 代表最前2页或最后2页 # abs判断前后2页
        if page_num < 3 or page_num > query_set.paginator.num_pages - 2 or abs(query_set.number - page_num) <= 2:
            element_class = ''
            if query_set.number == page_num:
                added_dot_ele = False
                element_class = 'active'
            # page_btns += '''<li class="%s"><a href="?page=%s">%s</a></li>''' %(element_class,page_num,page_num)
            # page_btns += '''<li class="%s"><a href="?page=%s%s&_q=%s">%s</a></li>''' %(element_class,page_num,filters,search_text,page_num)
            page_btns += '''<li class="{0}"><a href="?page={1}{2}&_q={3}&o={4}">{5}</a></li>'''.format(element_class, page_num, filters, search_text, order_by_text, page_num)
        else:# 显示...
            # 第一次进入循环的时候加上...
            # 如果做一个标志位
            if added_dot_ele == False:# 现在还没加...
                page_btns += '<li><a>...</a></li>'
                added_dot_ele = True
    return mark_safe(page_btns)

#-----------------过滤条件处理-------------------------
@register.simple_tag
def render_filter_element(filter_field, admin_class, filter_conditions):
    # 初始化下拉框
    # select_element = """<select class='form-control' name={0}><option value=''>-----</option>""".format(filter_field)
    select_element = """<select class='form-control' name={filter_field}><option value=''>-----</option>"""

    # 获取字段
    field_object = admin_class.model._meta.get_field(filter_field)
    # 字段处理
    # 默认不选中
    selected = ''
    # choice处理
    if field_object.choices:
        # 遍历choices值
        for choice_item in field_object.get_choices()[1:]:
            #判断选择条件是否和choice值相等
            if filter_conditions.get(filter_field) == str(choice_item[0]):
                # 被选中
                selected = 'selected'
            select_element += """<option value='{0}' {1}>{2}</option>""".format(choice_item[0],selected, choice_item[1])

            selected = ''
    # 外键处理
    if type(field_object).__name__ == 'ForeignKey':
        for choice_item in field_object.get_choices()[1:]:
            # 判断选择条件是否和choice值相等
            if filter_conditions.get(filter_field) == str(choice_item[0]):
                # 被选中
                selected = 'selected'
            select_element += """<option value='{0}' {1}>{2}</option>""".format(choice_item[0], selected, choice_item[1])
            selected = ''
    if type(field_object).__name__ in ['DateTimeField','DateField']:
        date_els = []
        today_ele = datetime.now().date()
        date_els.append(['今天', datetime.now().date()])
        date_els.append(['昨天', today_ele - timedelta(days=1)])
        date_els.append(['近七天', today_ele - timedelta(days=7)])
        date_els.append(['本月', today_ele.replace(day=1)])
        date_els.append(['近30天', today_ele - timedelta(days=30)])
        date_els.append(['近90天', today_ele - timedelta(days=90)])
        date_els.append(['近180天', today_ele - timedelta(days=180)])
        date_els.append(['本年', today_ele.replace(month=1,day=1)])
        date_els.append(['近一年', today_ele - timedelta(days=365)])

        selected = ''

        for item in date_els:
            select_element += """<option value='{0}' {1}>{2}</option>""".format(item[1], selected, item[0])

        # filter_field_name = "%s__gte" %filter_field
        filter_field_name = "{0}__gte".format(filter_field)

    else:
        filter_field_name = filter_field
    select_element += '</select>'
    select_element = select_element.format(filter_field=filter_field_name)


    return mark_safe(select_element)


#---------------------创建表头----------------------------
@register.simple_tag
def create_table_title(title_name, order_by_text, filter_conditions,admin_class):
    # 过滤条件
    filters = ''
    for k, v in filter_conditions.items():
        filters += "&{0}={1}".format(k, v)
    # 标签元素
    element = '''<th><a href="?{filters}&o={order_by_text}">{title_name}</a>{sort_icon}</th>'''
    # 判断排序数据
    if order_by_text:
        # 升序箭头
        if order_by_text.startswith("-"):
            sort_icon = '''<span class="glyphicon glyphicon-chevron-up"></span>'''
        # 降序箭头
        else:
            sort_icon = '''<span class="glyphicon glyphicon-chevron-down"></span>'''
        # 对比字段
        if order_by_text.strip("-") == title_name:# 排序的就是这个字段
            order_by_text = order_by_text
        else:
            order_by_text = title_name
            sort_icon = '' #如果没有匹配上就不显示箭头
    else: # 没有排序
        order_by_text = title_name
        sort_icon = ''
    try:
        column_verbose_name = admin_class.model._meta.get_field(title_name).verbose_name.upper()
    except FieldDoesNotExist as e:
        column_verbose_name = getattr(admin_class,title_name).display_name
        element = '''<th><a href="javascript:void(0);">{title_name}</a></th>'''.format(title_name=column_verbose_name)
        return mark_safe(element)
    ele = element.format(order_by_text=order_by_text,title_name=column_verbose_name, sort_icon=sort_icon, filters=filters)

    return mark_safe(ele)


@register.simple_tag
def get_model_name(admin_class):
    return admin_class.model._meta.verbose_name_plural

@register.simple_tag
def get_m2m_obj_list(admin_class, field,form_obj):
    """
    返回m2m所有待选数据
    :param admin_class:
    :param field:
    :return:
    """
    # 表结构对象的某个字段
    field_obj = getattr(admin_class.model, field.name)
    all_data_list = field_obj.rel.model.objects.all()

    # 单条数据的对象中的某个字段
    if form_obj.instance.id:
        obj_instance_field = getattr(form_obj.instance,field.name)
        selected_obj_list = obj_instance_field.all()
    else:# 代表这是在创建一条新的记录
        return all_data_list

    standby_obj_list = []
    for obj in all_data_list:
        if obj not in selected_obj_list:
            standby_obj_list.append(obj)

    return standby_obj_list


@register.simple_tag
def get_m2m_selected_obj_list(form_obj,field):
    """
    返回已选择的m2m数据
    :param form_obj:
    :param field:
    :return:
    """
    if form_obj.instance.id:
        field_obj = getattr(form_obj.instance,field.name)
        return field_obj.all()

@register.simple_tag
def print_obj_methods(obj):
    print("-------------debug %s-----------" % obj)
    print(dir(obj))


def recursive_related_objs_lookup(objs):
    # model_name = objs[0]._meta.model_name
    ul_ele = "<ul>"
    for obj in objs:
        # strip("<>")的意义，如果不写return mark_safe()的时候会把数据当做标签来处理
        li_ele = '''<li> %s : %s </li>''' %(obj._meta.verbose_name_plural,obj.__str__().strip("<>"))
        ul_ele  += li_ele

        # print("#######obj._meta.local_many_to_many",obj._meta.local_many_to_many)
        # 把所有跟这个对象直接关联的m2m字段取出来
        for m2m_field in obj._meta.local_many_to_many:
            sub_ul_ele = "<ul>"
            m2m_field_obj = getattr(obj,m2m_field.name) # 相当于getattr(customer,'tags')

            for o in m2m_field_obj.select_related(): # customer.tags.select_related()
                li_ele = '''<li> %s : %s </li>''' %(m2m_field.verbose_name,o.__str__().strip("<>"))
                sub_ul_ele += li_ele

            sub_ul_ele += "</ul>"
            ul_ele += sub_ul_ele # 最终跟最外层的ul相拼接




        for related_obj in obj._meta.related_objects:
            if 'ManyToManyRel' in related_obj.__repr__():
                if hasattr(obj,related_obj.get_accessor_name()): # hasattr(customer,'enrollment_set')
                    accessor_obj = getattr(obj,related_obj.get_accessor_name())
                # 上面accessor_obj 相当于 customer.enrollment_set

                    if hasattr(accessor_obj,'select_related'): # select_related() = all()
                        target_objs = accessor_obj.select_related()
                        # 上面target_objs 相当于 customer.enrollment_set.all()

                        sub_ul_ele = "<ul style='color: red'>"
                        for o in target_objs:
                            li_ele = '''<li> %s : %s </li>''' %(o._meta.verbose_name,o.__str__().strip("<>"))
                            sub_ul_ele += li_ele

                        sub_ul_ele += "</ul>"
                        ul_ele += sub_ul_ele


            elif hasattr(obj,related_obj.get_accessor_name()): # hasattr(customer,'enrollment_set')
                accessor_obj = getattr(obj,related_obj.get_accessor_name())
                # 上面accessor_obj 相当于 customer.enrollment_set

                if hasattr(accessor_obj,'select_related'): # select_related() = all()
                    target_objs = accessor_obj.select_related()
                    # 上面target_objs 相当于 customer.enrollment_set.all()

                else:
                    print("one to one i guess:",accessor_obj)
                    target_objs = accessor_obj

                if len(target_objs) > 0:
                    nodes = recursive_related_objs_lookup(target_objs)
                    ul_ele += nodes
    ul_ele += "</ul>"
    return ul_ele




@register.simple_tag
def display_obj_related(objs):
    """
    把对象及所有相关联的数据取出来
    :param objs:
    :return:
    """

    # objs = [objs,] # fake

    if objs:
        model_class = objs[0]._meta.model
        mode_name = objs[0]._meta.model_name
        return mark_safe(recursive_related_objs_lookup(objs))

@register.simple_tag
def get_action_verbose_name(admin_class,action):

    action_func = getattr(admin_class,action)

    return action_func.display_name if hasattr(action_func,'display_name') else action


















# -------------------------fengexian------------

@register.simple_tag
def get_horizontal_tag_values(field, admin_class, form_object):
    field_obj = getattr(admin_class.model, field.name)
    query_sets_all = field_obj.rel.to.objects.all()

    instance_field = getattr(form_object.instance, field.name)
    query_sets_select = instance_field.all()

    diff_query_sets = query_sets_all.difference(query_sets_select)
    return diff_query_sets

@register.simple_tag
def get_horizontal_field_value(field, form_object):
    print(form_object.instance.tags)
    field_obj = getattr(form_object.instance, field.name)
    selected_list = field_obj.all()
    return selected_list

@register.simple_tag
def get_m2m_object_list(admin_class, form_obj, field):
    """
    返回待选标签数据
    :param admin_class:
    :param form_obj:
    :param field:
    :return:
    """
    field_obj = getattr(admin_class.model, field.name)
    all_obj_list = field_obj.rel.model.objects.all()

    print('**form_obj.instance.id',form_obj.instance.id)
    if form_obj.instance.id:
        selected_field_obj = getattr(form_obj.instance, field.name)
        selected_obj_list = selected_field_obj.all()
    else:
        return all_obj_list

    standby_obj_list = []
    for obj in all_obj_list:
        if obj not in selected_obj_list:
            standby_obj_list.append(obj)

    return standby_obj_list

@register.simple_tag
def get_m2m_selected_object_list(form_obj, field):
    """
    返回已选标签数据
    :param form_obj:
    :param field:
    :return:
    """
    if form_obj.instance.id:
        field_obj = getattr(form_obj.instance, field.name)
        return field_obj.all()