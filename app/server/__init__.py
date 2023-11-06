import json

from app.db.models import Record, Include
from sqlalchemy import and_


def init_register(u_id: int):
    '''
    注册用户基本信息
    :param u_id:
    :return:
    '''
    from app import session
    try:
        record = Record(user_id=u_id)
        session.add(record)
        session.commit()

    except Exception as e:
        session.rollback()
    finally:
        session.close()


def check_user_exist(u_id: int) -> bool:
    '''
    检测用户是否存在
    :param u_id: 
    :return: 
    '''
    from app import session
    try:
        record = session.query(Record).filter(Record.user_id == str(u_id)).first()
        if record is None:
            return False
    finally:
        session.close()

    return True


def check_notice_setting(u_id: int) -> bool:
    '''
    检测是否配置了通知群或频道
    :param u_id:
    :return:
    '''
    from app import session
    try:
        record = session.query(Record).filter(Record.user_id == str(u_id)).first()
        if record.notice_group_id is None:
            return False
    finally:
        session.close()

    return True


def add_notice_group(u_id: int, notice_group_id: str):
    '''
    检测用户是否存在
    :param u_id:
    :return:
    '''
    from app import session

    try:
        session.query(Record).filter(Record.user_id == str(u_id)).update({'notice_group_id': notice_group_id})
        session.commit()
    except Exception as e:
        session.rollback()
    finally:
        session.close()


def query_decord(u_id: int) -> Record:
    from app import session

    try:
        if check_user_exist(u_id):
            return session.query(Record).filter(Record.user_id == str(u_id)).first()
    finally:
        session.close()


def do_start_notice(u_id: int):
    '''
    启动通知
    :param u_id:
    :return:
    '''
    from app import session
    try:
        session.query(Record).filter(Record.user_id == str(u_id)).update({'status': 1})
        session.commit()
    except Exception as e:
        session.rollback()
    finally:
        session.close()


def do_shutdown_notice(u_id: int):
    '''
    关闭通知
    :param u_id:
    :return:
    '''
    from app import session
    try:
        session.query(Record).filter(Record.user_id == str(u_id)).update({'status': 0})
        session.commit()
    except Exception as e:
        session.rollback()
    finally:
        session.close()


def update_include_list(u_id: int, g_id: int, include: list):
    '''
    更新通知新用户
    :param exclude:
    :return:
    '''
    from app import session
    include = json.dumps(include)
    try:
        session.query(Include).filter(and_(Include.user_id == str(u_id), Include.group_id == str(g_id))).update(
            {'include': include})
        session.commit()
    except Exception as e:
        session.rollback()
    finally:
        session.close()


def query_decord_include(u_id: int, g_id: int) -> Include:
    '''
    查询通知包含
    :param exclude:
    :return:
    '''
    from app import session

    try:
        if check_user_exist(u_id):
            return session.query(Include).filter(
                and_(Include.user_id == str(u_id), Include.group_id == str(g_id))).first()
    finally:
        session.close()


def add_decord_include(u_id: int, g_id: int, include: list):
    '''
    添加通知新用户
    :param exclude:
    :return:
    '''
    from app import session
    include = json.dumps(include)
    try:
        include_record = Include(user_id=u_id, group_id=g_id, include=include)
        session.add(include_record)
        session.commit()
    except Exception as e:
        session.rollback()
    finally:
        session.close()


def setting_token(u_id: int, token: str):
    '''
    配置token
    :param u_id:
    :param token:
    :return:
    '''
    from app import session
    try:
        session.query(Record).filter(Record.user_id == str(u_id)).update({'token': token})
        session.commit()
    except Exception as e:
        session.rollback()
    finally:
        session.close()