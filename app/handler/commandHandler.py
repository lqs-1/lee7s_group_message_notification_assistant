# Update:从Telegram获取更新
import json
import logging
import re
from datetime import datetime


from telegram import Update
# ContextTypes:上下文类型
from telegram.ext import ContextTypes

from app.server import init_register, check_user_exist, add_notice_group, query_decord, do_start_notice, \
    do_shutdown_notice, check_notice_setting, query_decord_include, update_include_list, add_decord_include, \
    setting_token
from app.utils.token_utils import _check_token, _generate_token

PAGE_SIZE = 1


# register命令
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''响应register命令
    保存用户基本信息
    '''

    if update.message.chat.type.title() == 'Private':
        # 用户id
        u_id = update.message.chat.id

        if check_user_exist(u_id):
            logging.warning(f"用户 {update.message.chat.username} 重复注册 无效")

            return await context.bot.send_message(chat_id=update.effective_chat.id, text="请勿重复注册")

        init_register(u_id)

        logging.warning(f"用户 {update.message.chat.username} 初始化注册成功")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="注册成功")

    else:
        logging.warning(f"用户 {update.message.chat.username} 初始化注册 但是走错地方了")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="此命令只可在机器人页面个人使用")



# help命令
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''响应help命令'''

    text = '使用此机器人需要注意几点:\n' \
           '1.需要进项消息提示的群必须是使用者的 也就是你是群主 并且机器人需要访问消息 也就是说这个机器人是面向群主的 群成员使用没有效果\n' \
           '2.通知群或者频道要将机器人设置成管理员\n' \
           '3.被通知的群可以由多个 通知群只能有一个\n' \
           '4.只会通知在机器人进群配置好以后进来的用户的信息\n\n' \
           '/register 初始化注册 将用户账号添加到系统中\n' \
           '/cat 查看配置 可以查看配置的通知群或者通知频道的ID还有自己的ID\n' \
           '/notice 格式 /notice xxxxxxxxxxxxx 配置通知群或者通知频道ID\n' \
           '/do_start 开启消息通知\n' \
           '/do_shutdown 关闭消息通知\n' \
           '/token 格式 /token xxxxxxxx 配置token\n' \
           '/check_token 查看token过期时间\n' \
           '/generate_token 管理员生成token\n' \

    logging.warning(f"用户 {update.message.chat.username} 获取了帮助信息")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


# cat命令
async def cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''响应cat命令'''
    if update.message.chat.type in ['group', 'supergroup']:
        logging.warning(f"用户 {update.message.from_user.username} 群内查看配置 被拒绝")
        return await context.bot.send_message(chat_id=update.effective_chat.id, text="此命令机器人页面使用")


    record = query_decord(update.effective_chat.id)

    if record is None:
        return await context.bot.send_message(chat_id=update.effective_chat.id, text='请前去注册 /register')

    result = f'u_id: {record.user_id}\n' \
             f'通知群id: {record.notice_group_id}\n' \
             f'状态: {record.status} <0表示关闭 1表示开启>\n' \
             f'token寿命: {_check_token(record.token).get("expire")}'

    logging.warning(f"用户 {update.message.chat.username} 查看了配置")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=result)



# notice命令
async def notice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''响应notice命令'''
    if update.message.chat.type in ['group', 'supergroup']:
        logging.warning(f"用户 {update.message.from_user.username} 群内配置通知 被拒绝")

        return await context.bot.send_message(chat_id=update.effective_chat.id, text="此命令机器人页面使用")

    if len(update.message.text.split(" ")) >= 2:

        notice_group_id = update.message.text.split(" ")[-1]

        if check_user_exist(update.effective_chat.id):

            decord = query_decord(update.effective_chat.id)

            if decord.token is None:
                return await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="请先设置token参数 /token xxxxxxx 联系客服 @lee7s_7s")
            elif _check_token(decord.token).get('expire', None) is None:
                return await context.bot.send_message(chat_id=update.effective_chat.id,
                                                      text="token无效请联系客服 @lee7s_7s")
            elif datetime.strptime(_check_token(decord.token).get('expire'), "%Y-%m-%d %H:%M:%S") < datetime.now():
                return await context.bot.send_message(chat_id=update.effective_chat.id,
                                                  text="token无效请联系客服 @lee7s_7s")


            notice_group_id_str = str(notice_group_id)

            # print(notice_group_id)

            if not re.match(r'^-\d{13}', notice_group_id_str):

                return await context.bot.send_message(chat_id=update.effective_chat.id, text="id不可用,请重新配置")

            try:
                await context.bot.getChatMember(notice_group_id, context.bot.id)
            except Exception as e:
                return await context.bot.send_message(chat_id=update.effective_chat.id, text="请先把机器人拉进群再配置")

            add_notice_group(update.effective_chat.id, notice_group_id)

            logging.warning(f"用户 {update.message.chat.username} 配置通知成功")

            return await context.bot.send_message(chat_id=update.effective_chat.id, text="配置成功,重复配置为更新")

        return await context.bot.send_message(chat_id=update.effective_chat.id, text="请先 /register 初始化注册")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="请添加id参数")



# 消息提示处理器
async def group_message_notice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''消息提示'''
    # print(update.message.chat.type)
    if update.message.chat.type in ['group', 'supergroup']:
        # 群组id
        g_id = update.message.chat.id


        admins = await update.message.chat.get_administrators()

        if len(admins) == 2:
            user_id = admins[1].user.id
        else:
            user_id = admins[0].user.id

        record = query_decord(user_id)

        if record is None:
            return
        elif record.notice_group_id is None:
            return

        include = query_decord_include(user_id, g_id)

        if include is None:
            return

        if record.status == 0:
            pass
        else:

            if g_id != int(record.notice_group_id):

                if record.token is None:
                    return await context.bot.send_message(chat_id=user_id,
                                                          text="推送失败 请先设置token参数 /token xxxxxxx 联系客服 @lee7s_7s")
                elif _check_token(record.token).get('expire', None) is None:
                    return await context.bot.send_message(chat_id=user_id,
                                                      text="token无效请联系客服 @lee7s_7s")
                elif datetime.strptime(_check_token(record.token).get('expire'), "%Y-%m-%d %H:%M:%S") < datetime.now():
                    return await context.bot.send_message(chat_id=user_id,
                                                      text="token无效请联系客服 @lee7s_7s")

                include_list = json.loads(include.include)

                if update.message.from_user.id in include_list:
                    # 群组名称
                    g_name = update.message.chat.title

                    g_account = update.message.chat.username

                    u_id = update.message.from_user.id

                    u_account = update.message.from_user.username

                    u_nic_first = update.message.from_user.first_name
                    u_nic_last = update.message.from_user.last_name

                    u_nic = u_nic_first + u_nic_last if u_nic_last is not None else u_nic_first

                    message_id = update.message.message_id

                    result = f'🎉有新用户发言🎉\n' \
                             f'群  组: {g_name}\n' \
                             f'群链接: @{g_account}\n' \
                             f'群组ID: {g_id}\n' \
                             f'发言昵称: {u_nic}\n' \
                             f'发言账号: @{u_account}\n' \
                             f'发言ID: {u_id}\n' \
                             f'信 息: https://t.me/{g_account}/{message_id}\n'
                    logging.warning(f"用户 {update.message.from_user.username} 的群 {g_name} 有消息 \n {result}")

                    return await context.bot.send_message(chat_id=record.notice_group_id, text=result)






# 启动
async def do_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''启动消息提示'''
    if update.message.chat.type in ['group', 'supergroup']:
        logging.warning(f"用户 {update.message.from_user.username} 群内开启通知 被拒绝")

        return await context.bot.send_message(chat_id=update.effective_chat.id, text="此命令机器人页面使用")
    if check_user_exist(update.effective_chat.id):

        if check_notice_setting(update.effective_chat.id):

            do_start_notice(update.effective_chat.id)

            logging.warning(f"用户 {update.message.from_user.username} 开启了通知")

            return await context.bot.send_message(chat_id=update.effective_chat.id, text="通知已开启")

        return await context.bot.send_message(chat_id=update.effective_chat.id, text="请先配置通知 /notice")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="请先 /register 初始化注册")


# 关闭
async def do_shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''关闭消息提示'''
    if update.message.chat.type in ['group', 'supergroup']:
        logging.warning(f"用户 {update.message.from_user.username} 群内关闭通知 被拒绝")

        return await context.bot.send_message(chat_id=update.effective_chat.id, text="此命令机器人页面使用")

    if check_user_exist(update.effective_chat.id):

        if check_notice_setting(update.effective_chat.id):
            do_shutdown_notice(update.effective_chat.id)

            logging.warning(f"用户 {update.message.from_user.username} 关闭了通知")

            return await context.bot.send_message(chat_id=update.effective_chat.id, text="通知已关闭")

        return await context.bot.send_message(chat_id=update.effective_chat.id, text="请先配置通知 /notice")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="请先 /register 初始化注册")


async def new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.new_chat_members:

        new_members = update.message.new_chat_members

        g_id = update.message.chat.id

        admins = await update.message.chat.get_administrators()

        if len(admins) == 2:

            user_id = admins[1].user.id

        else:

            user_id = admins[0].user.id

        record = query_decord(user_id)

        if record is None:
            return

        elif record.notice_group_id is None:
            return

        if g_id != record.notice_group_id:

            include = query_decord_include(user_id, g_id)

            if include is not None:
                # 里面存放各个群的排除列表 每一项都是一个字典
                include_list = json.loads(include.include)

                # print(g_id)
                for member in new_members:
                    member_id = member.id

                    if member_id not in include_list:
                        logging.warning(f"用户 {update.message.from_user.username} 添加新用户 {member_id} 的通知")
                        include_list.append(member_id)
                        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"@{member.username} 欢迎欢迎🎉🎉")

                update_include_list(user_id, g_id, include_list)

            else:
                include_list = list()
                for member in new_members:
                    logging.warning(f"用户 {update.message.from_user.username} 添加新用户 {member.id} 的通知")
                    member_id = member.id
                    include_list.append(member_id)
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"@{member.username} 欢迎欢迎🎉🎉")

                add_decord_include(user_id, g_id, include_list)



async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    配置token
    :param update:
    :param context:
    :return:
    '''

    if update.message.chat.type in ['group', 'supergroup']:
        logging.warning(f"用户 {update.message.from_user.username} 群内配置token 被拒绝")

        return await context.bot.send_message(chat_id=update.effective_chat.id, text="此命令机器人页面使用")

    if len(update.message.text.split(" ")) >= 2:

        token = update.message.text.split(" ")[-1]

        # print(token)

        data = _check_token(token)

        if data.get('expire', None) is None:
            return await context.bot.send_message(chat_id=update.effective_chat.id, text="token无效请联系客服 @lee7s_7s")
        elif datetime.strptime(data.get('expire'), "%Y-%m-%d %H:%M:%S") < datetime.now():
            return await context.bot.send_message(chat_id=update.effective_chat.id, text="token无效请联系客服 @lee7s_7s")

        setting_token(update.effective_chat.id, token)

        logging.warning(f"用户 {update.message.from_user.username} 配置token成功")

        return await context.bot.send_message(chat_id=update.effective_chat.id, text="token配置成功 可以使用 /check_token 验证")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="请添加token参数 没有token请联系客服 @lee7s_7s")



async def check_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    校验token
    :param update:
    :param context:
    :return:
    '''

    if update.message.chat.type in ['group', 'supergroup']:
        logging.warning(f"用户 {update.message.from_user.username} 群内校验token 被拒绝")

        return await context.bot.send_message(chat_id=update.effective_chat.id, text="此命令机器人页面使用")

    decord = query_decord(update.effective_chat.id)

    if decord is None:
        return await context.bot.send_message(chat_id=update.effective_chat.id, text='请前去注册 /register')

    if decord.token is not None:
        data = _check_token(decord.token)

        logging.warning(f"用户 {update.message.from_user.username} 校验了token")

        if datetime.strptime(data.get('expire'), "%Y-%m-%d %H:%M:%S") > datetime.now():
            return await context.bot.send_message(chat_id=update.effective_chat.id, text=f"您的token有效,过期时间 {data.get('expire')}")
        else:
            return await context.bot.send_message(chat_id=update.effective_chat.id, text=f"您的token已过期,过期时间 {data.get('expire')},请联系客服 @lee7s_7s")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="请先设置token参数 /token xxxxxxx 联系客服 @lee7s_7s")


async def generate_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    生成token
    :param update:
    :param context:
    :return:
    '''
    if update.message.chat.type in ['group', 'supergroup']:
        logging.warning(f"用户 {update.message.from_user.username} 群内使用生成token 被拒绝")

        return await context.bot.send_message(chat_id=update.effective_chat.id, text="此命令机器人页面使用")

    if update.message.chat.type == 'private' and update.effective_chat.id == 5060527090:

        logging.warning(f"用户 {update.message.from_user.username} 管理员 调用生成token")

        return await context.bot.send_message(chat_id=update.effective_chat.id, text=_generate_token())

    await context.bot.send_message(chat_id=update.effective_chat.id, text="你无法使用此命令 生成token请联系 @lee7s_7s")


