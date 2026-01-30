listen_port = 111
post_url = "xxx"
stat_url = "xxx"

# 非群号的配置，此处写使用者和bot账号的id
owner_id = 114
bot_id = 514


class Groups:
    """QQ群分组管理"""
    g1 = 114
    g2 = 514
    g3 = 1919810
#作用群的群号

approve_requirements = {
    Groups.g1: {"prompt": "ksm_mc", "level": 1},
    Groups.g2: {"prompt": "riic"},
    Groups.g3: {"prompt": "riic"},
}
#分组管理