import os

DB_NAME = f"sqlite:///{os.path.dirname(os.path.dirname(__file__))}/rss_bot.db"

RUM_PORT = 62663
jwt_token = ""
ip = "127.0.0.1"

APIHOST = f"http://{ip}:{RUM_PORT}?jwt={jwt_token}"
SEEDURL = (
    f"rum://seed?v=1&e=0&n=0&b=fDLEJaQbSguWukji6IFjdQ&c=nZ4Tzjt39q4dpOXvFdlP8i535QncTjvdcPp0NfOpmSs&g=O7ejvtFFRK-Uz-ZLmS_48A&k=CAISIQKm%2BgTifqG6ga1FUb9NzXDetFIi9AosQSx%2FRBFH3RbGFQ%3D%3D&s=MEYCIQDlshiApdymHMDK65Qv9VqGevyspb3WW9cLcbHF0r7QagIhAMCxvEREmkQi2IReMu9OBx1rjSJvEcq510CywXYYsWHx&t=Fq-eR5Mpg6k&a=%E5%8E%BB%E4%B8%AD%E5%BF%83%E5%BE%AE%E5%8D%9A&y=group_timeline&u="
    + APIHOST
)
RUM_ASSET_ID = "4f2ec12c-22f4-3a9e-b757-c84b6415ea8f"
MY_XIN_USER_ID = "bae95683-eabb-422f-9588-24dadffd0323"
MY_RUM_GROUP_ID = "4e784292-6a65-471e-9f80-e91202e3358c"
COMMON_RUM_GROUP_ID = "3bb7a3be-d145-44af-94cf-e64b992ff8f0"
RUM_REWARD_BASE_NUM = 0.0001

# fake data for test, please update: create the group and get the group info.

COMMON_ACCOUNT_PWD = "27ab3bcd-3a32-4bff-9778-0d4a5c776925"

######## for rss #############################

DEFAULT_MINUTES = -60

RSS_BOT_COMMANDS = {
    "0": {"text": "取消所有订阅", "group_id": None},
    "1": {
        "text": "订阅 去中心微博",
        "group_id": "3bb7a3be-d145-44af-94cf-e64b992ff8f0",
        "minutes": DEFAULT_MINUTES,
    },
    "2": {
        "text": "订阅 Huoju在Rum上说了啥",
        "group_id": "f1bcdebd-4f1d-43b9-89d0-88d5fc896660",
        "minutes": DEFAULT_MINUTES,
    },
    "3": {
        "text": "订阅 去中心推特",
        "group_id": "bd119dd3-081b-4db6-9d9b-e19e3d6b387e",
        "minutes": DEFAULT_MINUTES,
    },
    "4": {
        "text": "订阅 RUM流动池与汇率",
        "group_id": "0be13ee2-10dc-4e3a-b3ba-3f2c440a6436",
        "minutes": int(DEFAULT_MINUTES * 0.25),
    },
    "5": {
        "text": "订阅 MOB流动池与汇率",
        "group_id": "dd90f5ec-2f63-4cff-b838-91695fe9150f",
        "minutes": int(DEFAULT_MINUTES * 0.25),
    },
    "10": {
        "text": "订阅 刘娟娟的朋友圈",
        "group_id": "4e784292-6a65-471e-9f80-e91202e3358c",
        "minutes": DEFAULT_MINUTES,
    },
    "11": {
        "text": "订阅 杰克深的朋友圈",
        "group_id": "cfb42114-0ee1-429b-86e5-7659108972be",
        "minutes": DEFAULT_MINUTES,
    },
    "12": {
        "text": "订阅 老子到处说",
        "group_id": "c2ed5dff-321b-4020-a80e-f3f2e70cc2a1",
        "minutes": DEFAULT_MINUTES,
    },
    "20": {
        "text": "订阅 每天一分钟，知晓天下事",
        "group_id": "a6aac332-7c8d-4632-bf3c-725368bb89d5",
        "minutes": DEFAULT_MINUTES,
    },
    "99": {"text": "订阅以上所有", "group_id": -1},
}


def check_groups():
    groups = {}
    for k in RSS_BOT_COMMANDS:
        _gid = RSS_BOT_COMMANDS[k]["group_id"]
        if _gid not in (None, -1):
            groups[_gid] = {
                "group_id": _gid,
                "group_name": RSS_BOT_COMMANDS[k]["text"].split("订阅 ")[1],
                "minutes": RSS_BOT_COMMANDS[k].get("minutes") or DEFAULT_MINUTES,
            }
    return groups


RSS_GROUPS = check_groups()


ADDS_TEXT = "\n👨‍👩‍👧‍👦 获取最佳用户体验，安装 Rum Apps 🥂: https://rumsystem.net/apps\n"


WELCOME_TEXT = "👋 hello 输入数字，订阅相应的种子网络" + (
    "\n🤖 输入数字的负数，取消订阅该种子网络，比如 10 的负数是 -10\n\n"
    + "\n".join([key + " " + RSS_BOT_COMMANDS[key]["text"] for key in RSS_BOT_COMMANDS])
    + "\n"
    + ADDS_TEXT
    + "\n如果您长时间未能收到任何动态，请反馈刘娟娟，或重新订阅。\n\n新增小工具：输入你的生日，比如“生日 1990 1 24”，将得到你这一辈子的数据（七年就是一辈子）。"
)
