import base64

import json


def decode(credit):
    salt = "9y78gpoERW4lBNYL"  # 盐值

    # 第一步：去除盐（salt）部分
    encode_credit = credit.replace(salt, "")

    # 第二步：Base64 解码
    credits = base64.b64decode(encode_credit).decode(
        "utf-8"
    )  # 解码后的内容转成 utf-8 字符串

    return json.loads(credits)
