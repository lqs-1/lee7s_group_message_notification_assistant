# CommandHandler:命令处理器
# MessageHandler:消息处理器
import logging

from telegram.ext import CommandHandler, MessageHandler, filters, ChatMemberHandler
from telegram.ext._application import Application
from app.handler.commandHandler import register, help, notice, cat, group_message_notice, do_start, do_shutdown, \
    new_chat_members, token, check_token, generate_token


def register_all_handler(application: Application):
    # 添加命令处理器

    logging.warning("application register 'register' command handler")
    application.add_handler(CommandHandler('register', register))

    logging.warning("application register 'help' command handler")
    application.add_handler(CommandHandler('help', help))

    logging.warning("application register 'notice' command handler")
    application.add_handler(CommandHandler('notice', notice))

    logging.warning("application register 'cat' command handler")
    application.add_handler(CommandHandler('cat', cat))

    logging.warning("application register 'do_start' command handler")
    application.add_handler(CommandHandler('do_start', do_start))

    logging.warning("application register 'do_shutdown' command handler")
    application.add_handler(CommandHandler('do_shutdown', do_shutdown))

    logging.warning("application register 'token' command handler")
    application.add_handler(CommandHandler('token', token))

    logging.warning("application register 'check_token' command handler")
    application.add_handler(CommandHandler('check_token', check_token))

    logging.warning("application register 'generate_token' command handler")
    application.add_handler(CommandHandler('generate_token', generate_token))

    logging.warning("application register 'new_member_join' handler")
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members))


    logging.warning("application register ALL message handler")
    application.add_handler(MessageHandler(filters.ALL, group_message_notice))


def new_chat_members_filter(update):
    return update.message.new_chat_members is not None