#coding:utf-8
from django.utils.translation import ugettext as _
from django.forms import ModelForm
from django.forms import ValidationError

def create_model_form(request, admin_class):
    """
    动态生成ModelForm类
    :param request:
    :param admin_class:
    :return:
    """
    #-----------类成员构造---------------
    class Meta:
        model = admin_class.model
        fields = "__all__"
        exclude = admin_class.modelform_exclude_fields
    # 类的成员
    attrs = {'Meta': Meta}

    #-----------动态创建类----------------
    #type函数创建类---》type('类名',(基类,),以字典形式的类的成员)
    _model_form_class = type('DynamicModelForm', (ModelForm,), attrs)

    #---------定义创建对象的方法---------------
    # 定义__new__方法，用于创建cls类名
    def __new__(cls, *args, **kwargs):
        # 遍历数据库的所有字段和字段对应的对象
        # base_field是个字典
        # print("__new__instance:",cls.instance)
        for field_name, field_obj in cls.base_fields.items():
            # 对字段对象的组件添加class属性
            field_obj.widget.attrs['class'] = 'form-control'
         # 创建当前类的实例---》即创建子类
            if not hasattr(admin_class,'is_add_form'):#代表这是添加form，不需要disabled
                if field_name in admin_class.readonly_fields:
                    field_obj.widget.attrs['disabled'] = 'disabled'

            if hasattr(admin_class,"clean_%s" %field_name):
                field_clean_func = getattr(admin_class,"clean_%s" %field_name)
                setattr(cls,"clean_%s" %field_name,field_clean_func)


        return ModelForm.__new__(cls)
        # 定义元数据


    def default_clean(self):
        """
        给所有的form默认加一个clean验证
        :param self:
        :return:
        """
        with open('1.html','at',encoding='utf-8') as f:
        #     print("---running default clean",admin_class,file=f)
        #     print("---running default clean",admin_class.readonly_fields,file=f)
            print("---obj instance",self.instance,file=f)

        error_list = []
        if self.instance.id: # 这是个修改的表单
            for field in admin_class.readonly_fields:
                field_val = getattr(self.instance,field) # val to db
                if hasattr(field_val,"select_related"): # m2m
                    m2m_objs = getattr(field_val,'select_related')().select_related()
                    m2m_vals = [i[0] for i in m2m_objs.values_list('id')]

                    set_m2m_vals = set(m2m_vals)
                    set_m2m_vals_from_frontend = set([i.id for i in self.cleaned_data.get(field)])
                    if set_m2m_vals != set_m2m_vals_from_frontend:
                        # error_list.append(ValidationError(
                        # _('Field %(field)s is readonly'),
                        # code='invalid',
                        # params={'field':field},
                        # ))
                        #
                        self.add_error(field,"readonly field")
                    continue


                field_val_from_frontend = self.cleaned_data.get(field)

                with open('1.html','at',encoding='utf-8') as f:
                    # print("cleaned data:",self.cleaned_data)
                    print("--field compare:",field, field_val,field_val_from_frontend,file=f)


                if field_val != field_val_from_frontend:
                    error_list.append(ValidationError(
                        _('Field %(field)s is readonly,data should be %(val)s'),
                        code='invalid',
                        params={'field':field,'val':field_val}
                    ))

        # readonly_table check
        if admin_class.readonly_table:
            raise ValidationError(
               _('Table is readonly ,can not be modified or added'),
                code='invalid',
            )

        # invoke user's customized form validation
        self.ValidationError = ValidationError
        response = admin_class.default_form_validation(self)
        if response:
            error_list.append(response)

        if error_list:
            raise ValidationError(error_list)
    #--------------为对象添加属性----------------
    #为该类添加__new__静态方法，当调用该类时，会先执行__new__方法，创建对象
    # 这里会覆盖父类的_-new__
    setattr(_model_form_class,'__new__', __new__)
    setattr(_model_form_class,'clean',default_clean)

    return _model_form_class

