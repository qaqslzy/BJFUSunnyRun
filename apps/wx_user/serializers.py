from rest_framework import serializers
import requests
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File

from .models import WxUser,StudentId
from utils.wx_fun import get_user_info
from utils.sunnyrun import valid

#注册用的Serializer
class WxUserRegSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    avatarUrl = serializers.CharField(write_only=True)
    def create(self, validated_data):
        users = WxUser.objects.filter(openid=validated_data['openid'])
        if users:
            user = users[0]
        else:
            user = WxUser()
            user.student = StudentId.objects.create(username=validated_data['username'],
                                                    password=validated_data['password']
                                                    , gender=validated_data['gender'])
            user.user_name = validated_data['user_name']
            user.openid = validated_data['openid']
            user.session_key = validated_data['session_key']
            user.save()
            r = requests.get(validated_data['avatarUrl'])
            if r.status_code == requests.codes.ok:
                img_temp = NamedTemporaryFile()
                img_temp.write(r.content)
                img_temp.flush()
                user.display_photo.save("image_{}.jpg".format(user.id), File(img_temp), save=True)
            user.save(update_fields=["display_photo"])

        return user

    def validate(self, attrs):
        try:
            attrs["gender"] = valid(username=attrs["username"])
        except:
            raise serializers.ValidationError({"error":"账号或密码错误"})

        info = get_user_info(attrs['code'])
        print(info)
        attrs["openid"] =  info['openid']
        attrs['session_key'] = info['session_key']

        del attrs['code']
        return attrs

    class Meta:
        model = WxUser
        fields = ("username","password","code","user_name","id","avatarUrl","display_photo")
        """
        username:学号
        user_name:昵称
        password:没啥用的密码
        avatarUrl:头像的地址
        """

class WxUnLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = WxUser
        fields = ("id")