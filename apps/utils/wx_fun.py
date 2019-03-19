import requests
import drfSunnyrun.settings as settings

def get_openid(code):
    info = requests.get(settings.WX_LOGIN_URL.format(settings.APPID,
                                                     settings.SECRET,code)).json()
    return info['openid']

def get_user_info(code):
    return requests.get(settings.WX_LOGIN_URL.format(settings.APPID,
                                                     settings.SECRET,code)).json()