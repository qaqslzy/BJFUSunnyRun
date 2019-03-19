from rest_framework import viewsets,mixins,status
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_encode_handler
from rest_framework import authentication
import os
import redis

from drfSunnyrun import settings
from utils import permissions
from .serializers import WxUserRegSerializer,WxUnLoginSerializer
from utils.authentication import JSONWebTokenAuthentication,jwt_payload_handler
from .models import WxUser,StudentId
# Create your views here.
#用户的注册
class WxRegViewSet(mixins.CreateModelMixin,viewsets.GenericViewSet):

    queryset = WxUser.objects.all()
    serializer_class = WxUserRegSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        #创建成功后在返回的json里添加 token 和 name

        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["user_name"] = user.user_name if user.user_name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

class WxUnloginSet(mixins.DestroyModelMixin,viewsets.GenericViewSet):
    serializer_class = WxUnLoginSerializer
    queryset = WxUser.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        id = instance.id
        studentid = instance.student.id
        #删除对应排行榜上的名词
        conn = redis.Redis(host=settings.REDIS_URL, port=settings.REDIS_PORT)
        conn.zrem(settings.ZSET_NAME,instance.user_name+'_$_{}'.format(instance.id))
        #删除微信id
        self.perform_destroy(instance)
        #删除学号密码
        StudentId.objects.filter(id = studentid).delete()
        #删除头像图片
        dp = os.path.join(settings.MEDIA_ROOT,"dp") + "/image_{}.jpg".format(id)
        if os.path.exists(dp):
            os.remove(dp)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

