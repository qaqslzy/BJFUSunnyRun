import redis
from rest_framework import mixins,viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication

from utils import permissions
from utils.authentication import JSONWebTokenAuthentication,jwt_payload_handler
from drfSunnyrun import settings

class RankViewSet(mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    PAGE_NUM = 15
    def retrieve(self, request, *args, **kwargs):
        print(kwargs)
        conn = redis.Redis(host=settings.REDIS_URL, port=settings.REDIS_PORT)
        tote = conn.zcard(settings.ZSET_NAME)
        #页数i
        i = int(kwargs['pk'])
        if i < 0:
            i = 1
        rank_dict = {}
        if tote > i * self.PAGE_NUM:
            rank_dict['next'] = settings.MY_URL.format(
                ("rank/{}/".format(i+1))
            )
        else:
            rank_dict['next'] = False
        #排行列表
        other_list = conn.zrevrange(settings.ZSET_NAME,(i-1)*self.PAGE_NUM,i*self.PAGE_NUM-1)

        rank_dict['other'] = []
        for other in other_list:
            l_other = other.decode().split('_$_')
            temp = {}
            # 头像的地址
            temp['dp'] = settings.MY_URL.format(
                ("media/dp/image_{}.jpg".format(l_other[1]))
            )
            # 对应的昵称
            temp['name'] = l_other[0]
            # 跑步的总里程
            temp['mileages'] = int(conn.zscore(settings.ZSET_NAME, other))

            rank_dict['other'].append(temp)

        #自己的成绩
        if i == 1:
            rank_dict['my'] = {}
            rank_dict['my']['name'] = request.user.user_name
            name_id  = request.user.user_name + '_$_{}'.format(request.user.id)
            rank_dict['my']['mileages'] = int(conn.zscore(settings.ZSET_NAME,name_id))
            rank_dict['my']['dp'] = settings.MY_URL.format(
                ("media/dp/image_{}.jpg".format(request.user.id))
            )
            rank_dict['my']['my_rank'] = tote - conn.zrank(settings.ZSET_NAME,name_id)

        return Response(rank_dict,status=status.HTTP_200_OK)




