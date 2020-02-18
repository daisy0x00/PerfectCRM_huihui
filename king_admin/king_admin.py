
from django.shortcuts import render,redirect,HttpResponse
from crm import models

# 数据结构容器
enabled_admins = {}
"""
{app名： {数据表名：界面需要显示的数据表管理类
        }
}
"""

# 创建基类
class BaseAdmin(object):
    list_display = []
    list_filter = []
    search_fields = []
    list_per_page = 20
    ordering = None
    filter_horizontal = []
    actions = ["delete_selected_objs",]
    readonly_fields = []
    readonly_table = False
    modelform_exclude_fields = []


    def delete_selected_objs(self,request,querysets):

        app_name =self.model._meta.app_label
        table_name = self.model._meta.model_name
        with open('1.html','at',encoding="utf-8") as f:
            print("---》delete_selected_objs",self,request,querysets,file=f)
        if self.readonly_table:
            errors = {"readonly_table": "This table is readonly,cannot be deleted or modified"}
        else:
            errors = {}

        if request.POST.get('delete_confirm') == "yes":
            if not self.readonly_fields:
                querysets.delete()
            return redirect("/king_admin/%s/%s" %(app_name,table_name))
        selected_ids = ','.join([str(i.id) for i in querysets])
        return render(request,"king_admin/table_obj_delete.html",{"objs":querysets,
                                                              "admin_class": self,
                                                              "app_name": app_name,
                                                              "table_name": table_name,
                                                              "selected_ids": selected_ids,
                                                              "action": request._admin_action,
                                                                  "errors":errors})

    def default_form_validation(self):
        """
        用户可以在此进行自定义的表单验证，相当于Django form的clean方法
        :return:
        """

        pass
# 自定义类，显示特定字段
class CustomerAdmin(BaseAdmin):
    # 显示字段
    list_display = ['id','qq','name','source','consultant','consult_course','date','status','enroll']
    # 过滤
    list_filters = ['source','consultant','consult_course','status', 'date']
    # 搜索功能，并指定搜索字段
    search_fields = ['qq', 'name', 'consultant__name']
    ordering = 'date'
    # 显示复选框
    filter_horizontal = ['tags']
    list_per_page = 6
    # model = models.Customer

    actions = ["delete_selected_objs","test"]
    # modelform_exclude_fields = []

    def test(self,request,querysets):
        print("in test")

    test.display_name = "测试动作"

    readonly_fields = ['qq','consultant','tags']
    # readonly_table = True

    def enroll(self):
        print("enroll",self.instance)
        if self.instance.status == 0:
            link_name = "报名新课程"
        else:
            link_name = "报名"
        return '''<a href="/crm/customer/%s/enrollment/">%s</a>''' %(self.instance.id,link_name)
    enroll.display_name = "报名链接"
    def default_form_validation(self):
        with open('1.html','at') as f:
            print("-----customer validation",self,file=f)
            print("---instance:",self.instance,file=f)

        consult_content = self.cleaned_data.get("content")
        if len(consult_content) < 15:
            return self.ValidationError(
                    ('Field %(field)s 咨询内容不能少于15个字符'),
                    code='invalid',
                    params={'field':"content",},
                )

    def clean_name(self):
        print("name clean validation: ", self.cleaned_data["name"])
        if not self.cleaned_data["name"]:
            self.add_error('name','can not be null')


class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ['customer','consultant','date']
    ordering = 'date'

class UserProfileAdmin(BaseAdmin):
    list_display = ['id','email','name',]
    ordering = 'id'
    readonly_fields = ('password',)

    filter_horizontal = ('user_permission','groups')
    modelform_exclude_fields = ['last_login']


class CourseRecordAdmin(BaseAdmin):
    list_display = ['from_class','day_num','teacher','has_homework','homework_title','date']
    ordering = 'date'

    def initialize_studyrecords(self,request,queryset):
        print("------>initialize_studyrecords",self,request,queryset)
        if len(queryset) > 1:
            return HttpResponse("只能选择一个班级")

        print(queryset[0].from_class.enrollment_set.all())
        new_obj_list = []
        for enroll_obj in queryset[0].from_class.enrollment_set.all():
            # models.StudyRecord.objects.get_or_create(
            #     student = enroll_obj,
            #     course_record = queryset[0],
            #     attendance = 0,
            #     score = 0,
            # )
            new_obj_list.append(models.StudyRecord(
                student = enroll_obj,
                course_record = queryset[0],
                attendance = 0,
                score = 0,
            ))
        try:
            models.StudyRecord.objects.bulk_create(new_obj_list) #批量创建
        except Exception as e:
            return HttpResponse("批量初始化学习记录失败，请检查该节课是否已经有对应的学习记录")

        return redirect("/king_admin/crm/studyrecord/?course_record=%s" %queryset[0].id)

    initialize_studyrecords.display_name = "初始化本节所有学员的上课记录"
    actions = ['initialize_studyrecords',]

class StudyRecordAdmin(BaseAdmin):
    list_display = ['id','student','course_record','attendance','score','date']
    ordering = 'date'
    list_filters = ['course_record','score','attendance']
    # list_editable = ['score','attendance']

# 构造数据结构---》通过models类和自定义类注册获取
def register(model_class,admin_class=None):
    if model_class._meta.app_label not in enabled_admins:
        enabled_admins[model_class._meta.app_label] = {}
        # enabled_admins['crm'] = {}
    # 添加自定义类属性为models类
    admin_class.model = model_class #绑定model对象和admin类
    # admin_obj = admin_class()
    # admin_obj.model = model_class

    # 通过表名获取到自定义类
    enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class # model_class._meta.app_label获取APP名，model_class._meta.model_name获取数据表名
    # enabled_admins['crm']['customerfollowup'] = CustomerFollowUpAdmin


# 进行注册构造数据结构
register(models.Customer,CustomerAdmin)
register(models.CustomerFollowUp,CustomerFollowUpAdmin)
register(models.UserProfile,UserProfileAdmin)
register(models.StudyRecord,StudyRecordAdmin)
register(models.CourseRecord,CourseRecordAdmin)


