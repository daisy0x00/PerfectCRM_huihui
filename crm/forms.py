from django.forms import ModelForm
from crm import models

class CustomerForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            # 对字段对象的组件添加class属性
            field_obj.widget.attrs['class'] = 'form-control'

            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs['disabled'] = 'disabled'
        return ModelForm.__new__(cls)

    def clean_qq(self):
        data = self.cleaned_data['qq']
        if self.instance.qq != data:
            self.add_error("qq","傻逼你还尝试黑我")
        return data

    class Meta:
        model = models.Customer
        fields = "__all__"
        exclude = ['tags','content','memo','status','referral_from','consult_course']
        readonly_fields = ['qq','consultant','source']

class PaymentForm(ModelForm):

    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            # 对字段对象的组件添加class属性
            field_obj.widget.attrs['class'] = 'form-control'
        return ModelForm.__new__(cls)

    class Meta:
        model = models.Payment
        fields = "__all__"

class EnrollmentForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            # 对字段对象的组件添加class属性
            field_obj.widget.attrs['class'] = 'form-control'
        return ModelForm.__new__(cls)

    class Meta:
        model = models.Enrollment
        fields = ['enrolled_class','consultant']