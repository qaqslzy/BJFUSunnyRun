import requests
import json


def valid(username):
    group_url = "http://bjfu.sunnysport.org.cn/api/student/group/{}".format(username)
    group = requests.get(group_url).json()
    if group['group'] == "Default_Male":
        sex = "male"
    elif group['group'] == "Default_Female":
        sex = "female"

    return sex

def score(username):
    score_url = "http://bjfu.sunnysport.org.cn/api/student/info/{}".format(username)
    score = requests.get(score_url).json()

    return score

