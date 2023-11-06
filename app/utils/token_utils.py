import datetime

from itsdangerous import URLSafeTimedSerializer

from app import config

# 创建 URLSafeTimedSerializer 对象
serializer = URLSafeTimedSerializer(secret_key=config.BotConfig.SECRET_KEY)


def _generate_token() -> str:
    # 生成 token
    data = dict()
    data.update({'expire': (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")})
    return serializer.dumps(data)


def _check_token(token) -> dict:
    # 验证 token
    try:
        return serializer.loads(token)  # 设置 token 的最大有效时间
    except Exception as e:
        return {}



if __name__ == '__main__':
    data = dict()
    data.update({'user_id': 12321431, 'time': (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")})

    # print(data)
    token = _generate_token()
    print(token)

    string = _check_token(token)
    print(datetime.datetime.strptime(string.get("expire"), "%Y-%m-%d %H:%M:%S") > datetime.datetime.now())