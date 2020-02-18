# coding:utf-8
from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
# Create your models here.


class Customer(models.Model):
    """
        客户信息表
    """
    name = models.CharField(max_length=32,blank=True,null=True,help_text="用户报名后请改为真实姓名")
    qq = models.CharField(max_length=64,unique=True)
    qq_name = models.CharField(max_length=64,blank=True,null=True)
    phone = models.CharField(max_length=64,blank=True,null=True)
    id_num = models.CharField(max_length=64,blank=True,null=True)
    email = models.EmailField(verbose_name="常用邮箱",blank=True,null=True)
    source_choices = ((0, '转介绍'),
                      (1, 'QQ群'),
                      (2, '官网'),
                      (3, '百度推广'),
                      (4, '51CTO'),
                      (5, '知乎'),
                      (6, '市场推广')
                      )

    source = models.SmallIntegerField(choices=source_choices,verbose_name='从什么途径了解的课程')
    referral_from = models.CharField(verbose_name="转介绍人qq",max_length=64,blank=True)
    consult_course = models.ForeignKey("Course",verbose_name="咨询课程",on_delete=models.CASCADE)
    content = models.TextField(verbose_name="咨询详情")
    tags = models.ManyToManyField("Tag",blank=True,null=True)
    status_choices = ((0,'已报名'),
                      (1,'未报名'),
                      )
    status = models.SmallIntegerField(choices=status_choices,default=1)
    consultant = models.ForeignKey("UserProfile",on_delete=models.CASCADE)
    memo = models.TextField(blank=True,null=True)
    date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.qq

    class Meta:
        verbose_name = "客户表"
        verbose_name_plural = "客户表"

    # def to_dict(self):
    #     name = self.name + 'vi'
    #     return {
    #         'name': name,
    #         'status': self.status,
    #         'status_text': self.get_status_display(),
    #         'id': self.id
    #     }

class Tag(models.Model):
    name = models.CharField(unique=True, max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"

class CustomerFollowUp(models.Model):
    """
        客户跟进表
    """
    customer = models.ForeignKey("Customer",on_delete=models.CASCADE)
    content = models.TextField(verbose_name="跟进内容")
    consultant = models.ForeignKey("UserProfile",on_delete=models.CASCADE)

    intention_choices = ((0, '2周内报名'),
                         (1, '1个月内报名'),
                         (2, '近期无报名计划'),
                         (3, '已在其他机构报名'),
                         (4, '已报名'),
                         (5, '已拉黑'),
                         )
    intention = models.SmallIntegerField(choices=intention_choices)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "<%s : %s>" %(self.customer.qq,self.intention)

    class Meta:
        verbose_name_plural = '客户跟进表'

class Course(models.Model):
    """
        课程表
    """
    name = models.CharField(max_length=64,unique=True)
    price = models.PositiveSmallIntegerField()
    period = models.PositiveSmallIntegerField(verbose_name="周期（月）")
    outline = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '课程表'

class Branch(models.Model):
    """
        校区
    """
    name = models.CharField(max_length=128,unique=True)
    addr = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '校区'

class ClassList(models.Model):
    """
        班级表
    """
    branch = models.ForeignKey("Branch",verbose_name="校区",on_delete=models.CASCADE)
    course = models.ForeignKey("Course",on_delete=models.CASCADE)
    class_type_choices = ((0, '面授（脱产）'),
                          (1, '面授（周末）'),
                          (2, '网络班')
                          )
    contract = models.ForeignKey("ContractTemplate",blank=True,null=True,on_delete=models.CASCADE)
    class_type = models.SmallIntegerField(choices=class_type_choices,verbose_name="班级类型")
    semester = models.PositiveSmallIntegerField(verbose_name="学期")
    teachers = models.ManyToManyField("UserProfile")
    start_date = models.DateField(verbose_name="开班日期")
    end_date = models.DateField(verbose_name="结业日期",blank=True,null=True)

    def __str__(self):
        return "%s %s %s" %(self.branch, self.course, self.semester)

    class Meta:
        unique_together = ('branch', 'course','semester')
        verbose_name_plural = '班级表'

class CourseRecord(models.Model):
    """
        上课记录
    """
    from_class = models.ForeignKey("ClassList",verbose_name="班级",on_delete=models.CASCADE)
    day_num = models.PositiveSmallIntegerField(verbose_name="第几节（天）")
    teacher = models.ForeignKey("UserProfile",on_delete=models.CASCADE)
    has_homework = models.BooleanField(default=True)
    homework_title = models.CharField(max_length=128,blank=True,null=True)
    homework_content = models.TextField(blank=True,null=True)
    outline = models.TextField(verbose_name="本节课程大纲")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s" %(self.from_class,self.day_num)

    class Meta:
        unique_together = ("from_class", "day_num")
        verbose_name_plural = '上课记录'

class StudyRecord(models.Model):
    """
        学习记录
    """
    student = models.ForeignKey("Enrollment",on_delete=models.CASCADE)
    course_record = models.ForeignKey("CourseRecord",on_delete=models.CASCADE)
    attendance_choices = ((0, '已签到'),
                          (1, '迟到'),
                          (2, '缺勤'),
                          (3, '早退'),
                          )
    attendance = models.SmallIntegerField(choices=attendance_choices,default=0)
    score_choices = ((100, 'A+'),
                     (90, 'A'),
                     (85, 'B+'),
                     (80, 'B'),
                     (75, 'B-'),
                     (70, 'C+'),
                     (60, 'C'),
                     (40, 'C-'),
                     (-50, 'D'),
                     (-100, 'COPY'),
                     (0, 'N/A'),    # not available
                     )
    score = models.SmallIntegerField(choices=score_choices)
    memo = models.TextField(blank=True,null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s %s" %(self.student,self.course_record,self.score)
    class Meta:
        unique_together = ('student','course_record')
        verbose_name_plural = '学习记录'

class Enrollment(models.Model):
    """
        报名表
    """
    customer = models.ForeignKey("Customer",on_delete=models.CASCADE)
    enrolled_class = models.ForeignKey("ClassList",verbose_name="所报班级",on_delete=models.CASCADE)
    consultant = models.ForeignKey("UserProfile",verbose_name="课程顾问",on_delete=models.CASCADE)
    contract_agreed = models.BooleanField(default=False,verbose_name="学员已同意合同条款")
    contract_approved = models.BooleanField(default=False,verbose_name="合同已审核")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" %(self.customer, self.enrolled_class)

    class Meta:
        unique_together = ("customer","enrolled_class")
        verbose_name_plural = '报名表'

class Payment(models.Model):
    """
        缴费记录
    """
    customer = models.ForeignKey("Customer",on_delete=models.CASCADE)
    course = models.ForeignKey("Course",verbose_name="所报课程",on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name="数额",default=500)
    consultant = models.ForeignKey("UserProfile",on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" %(self.customer,self.amount)

    class Meta:
        verbose_name_plural = '缴费记录'

# class UserProfile(models.Model):
#     """
#         账号表
#     """
#     user = models.OneToOneField(User,on_delete=models.CASCADE)
#     name = models.CharField(max_length=32)
#     roles = models.ManyToManyField("Role",blank=True,null=True)
#
#     def __str__(self):
#         return self.name

    # class Meta:
    #     verbose_name_plural = '账号表'

class ContractTemplate(models.Model):
    '''合同模板'''
    name = models.CharField("合同名称",max_length=64,unique=True)
    template = models.TextField()

    def __str__(self):
        return self.name

class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name
        )

        user.set_password(password)
        self.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_active = True
        user.is_admin = True
        user.save(using=self._db)
        return user

class UserProfile(AbstractBaseUser,PermissionsMixin):
    """
        账号表
    """
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    password = models.CharField(_('password'), max_length=128,
                                help_text=mark_safe('''<a href='password/'>修改密码</a>'''))
    name = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    roles = models.ManyToManyField("Role",blank=True)
    objects = UserProfileManager()

    stu_account = models.ForeignKey("Customer",verbose_name="关联学员账号",blank=True,null=True,
                                    help_text="只有学员报名后方可为其创建账号",on_delete=models.CASCADE)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class Role(models.Model):
    """
        角色表
    """
    name = models.CharField(max_length=32,unique=True)
    menus = models.ManyToManyField("Menu",blank=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '角色'


class Menu(models.Model):
    """
        菜单
    """
    name = models.CharField(max_length=32)
    url_type_choices = ((0,'alias'),(1,'absolute_url'))
    url_type = models.SmallIntegerField(choices=url_type_choices,default=0)
    url_name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    # class Meta:
    #     verbose_name_plural = '菜单栏'