"""drfSunnyrun URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url,include
from rest_framework.routers import DefaultRouter
from utils.jwt_views import obtain_jwt_token
from django.views.static import serve

from drfSunnyrun.settings import MEDIA_ROOT
from wx_user.views import WxRegViewSet,WxUnloginSet
from score.views import UserScoreViewSet
from rank_list.views import RankViewSet

router = DefaultRouter()
#注册和登陆
router.register(r'wx_reg',WxRegViewSet,base_name='wx_reg')
#查询成绩
router.register(r'score',UserScoreViewSet,base_name='score')
#退出登录
router.register(r'unlogin',WxUnloginSet,base_name='unlogin')
#排行榜
router.register(r'rank',RankViewSet,base_name='rank')

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    url(r'^', include(router.urls)),
    url(r'^login/', obtain_jwt_token),
]
