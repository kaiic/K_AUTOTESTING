from django.db import models

class BaseTable(models.Model):
    """
    公共字段列
    """

    class Meta:
        abstract = True
        verbose_name = "公共字段表"
        db_table = 'basetable'

    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)


class UserInfo(BaseTable):
    """
    用户注册信息表
    """

    class Meta:
        verbose_name = "用户信息"
        db_table = "userinfo"

    password = models.CharField('登陆密码', max_length=100, null=False)
    email = models.EmailField('用户邮箱', null=False)
    username = models.CharField('用户名', max_length=20, null=False)
    isadmin = models.IntegerField('是否管理员', null=False, default=0)
    status = models.IntegerField('状态', null=False, default=0)
    updater = models.CharField("修改人", max_length=20, null=True)


class UserToken(BaseTable):
    """
    用户登陆token
    """

    class Meta:
        verbose_name = "用户登陆token"
        db_table = "usertoken"

    user = models.OneToOneField(to=UserInfo, on_delete=models.CASCADE)
    token = models.CharField('token', max_length=50)