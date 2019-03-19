from django.db import models

# Create your models here.
class StudentId(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=50)
    #个人信息字段
    gender = models.CharField(max_length=6, choices=(("male", u"男"), ("female", "女")), default="female",
                              verbose_name="性别")

    class Meta:
        verbose_name = "学号"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

class WxUser(models.Model):
    #TODO 完善字段

    """
    用户
    """
    #第一次登陆时必补充字段
    user_name = models.CharField(max_length=100,verbose_name="昵称")
    display_photo = models.ImageField(null=True,blank=True,upload_to="dp/",verbose_name="头像")
    openid = models.CharField(unique=True,max_length=100)
    session_key = models.CharField(max_length=100)
    student = models.ForeignKey(StudentId,null=True,blank=True,verbose_name="账号密码",on_delete=models.CASCADE)

    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = verbose_name

    def get_username(self):
        return self.user_name

    def __str__(self):
        return self.user_name

