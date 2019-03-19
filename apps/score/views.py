from rest_framework import mixins,viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication
import redis

from drfSunnyrun import settings
from utils import permissions,sunnyrun
from utils.authentication import JSONWebTokenAuthentication,jwt_payload_handler
# Create your views here.

class UserScoreViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    def list(self, request, *args, **kwargs):

        try:
            score = sunnyrun.score(username=request.user.student.username)

            #将成绩加入 ZSET
            conn = redis.Redis(host=settings.REDIS_URL, port=settings.REDIS_PORT)
            conn.zadd(settings.ZSET_NAME,request.user.user_name
                      +'_$_{}'.format(request.user.id),score['mileages'])

            score['gender'] = request.user.student.gender
        except:
            return Response({"error":"账号或密码错误"},status = status.HTTP_401_UNAUTHORIZED)

        return Response(score, status=status.HTTP_200_OK)