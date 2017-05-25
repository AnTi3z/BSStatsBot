from config import *
import sqlite3
import logging
from time import strftime, gmtime


logger = logging.getLogger('BSstatbot')


def new_tlgr_user(user_id, user_name, first_name, last_name):
    try:
        with sqlite3.connect(SQLITE_DB_FILE) as conn:
            logger.debug(
                "INSERT or IGNORE into TlgrUser (UserID, UserName, FirstName, LastName) VALUES(%d,'%s','%s','%s')",
                user_id, user_name, first_name, last_name)
            curs = conn.execute('INSERT or IGNORE into TlgrUser (UserID, UserName, FirstName, LastName) VALUES(?,?,?,?)',
                         (user_id, user_name, first_name, last_name))
            if curs.rowcount == 0:
                logger.debug("UPDATE TlgrUser SET UserName='%s', FirstName='%s', LastName='%s' WHERE UserID=%d",
                             user_name, first_name, last_name, user_id)
                conn.execute('UPDATE TlgrUser SET UserName=?, FirstName=?, LastName=? WHERE UserID=?',
                             (user_name, first_name, last_name, user_id))
                logger.debug('User updated')
                return False
            else:
                logger.info('Tlgr user added: %d `%s %s` (@`%s`)', user_id, first_name, last_name, user_name)
                return True
    except sqlite3.IntegrityError:
        logger.warning('Ошибка добавления/обновления записи TlgrUser: %d `%s %s` (@`%s`)', user_id, first_name, last_name, user_name)
        return False


def new_game_user(user_name, tlgr_id=None):
    try:
        with sqlite3.connect(SQLITE_DB_FILE) as conn:
            logger.debug("INSERT or IGNORE into GameUser (UserName, TlgrID) VALUES('%s',%d)",
                         user_name, tlgr_id if tlgr_id else -1)
            curs = conn.execute('INSERT or IGNORE into GameUser (UserName, TlgrID) VALUES(?,?)', (user_name, tlgr_id))
            if curs.rowcount == 1:
                logger.info('Game user `%s` added', user_name)
                return True
            else:
                logger.debug('Game user already exist')
                return False
    except sqlite3.IntegrityError:
        logger.warning('Ошибка добавления записи GameUser')
        return False


def update_user_land(user_name, land_name):
    try:
        with sqlite3.connect(SQLITE_DB_FILE) as conn:
            logger.debug("UPDATE GameUser SET LandName='%s' WHERE UserName='%s'", land_name, user_name)
            conn.execute('UPDATE GameUser SET LandName=? WHERE UserName=?', (land_name, user_name))
            return True
    except sqlite3.IntegrityError:
        logger.warning('Ошибка обновления записи GameUser: `%s` из `%s`', user_name, land_name)
        return False


def new_battle(msg, user_name1, user_name2, win_flag, send_army, return_army, money, land, land_name2, karma):
    try:
        with sqlite3.connect(SQLITE_DB_FILE) as conn:
            logger.debug("INSERT or IGNORE into Battles "
                         "(ChatID, ForwarderID, FrwMessageTime, User1ID, User2ID, BattleTime, WinFlag, SendArmy, ReturnArmy, Money, Land, Karma) "
                         "VALUES(%d,%d,%d,"
                         "(SELECT ID FROM GameUser WHERE UserName = '%s'),"
                         "(SELECT ID FROM GameUser WHERE UserName = '%s'),"
                         "%d,%d,%d,%d,%d,%d,%d)",
                         msg.chat.id, msg.from_user.id, msg.date,
                         user_name1, user_name2,
                         msg.forward_date, 1 if win_flag else 2, int(send_army),
                         int(return_army) if return_army else 0, int(money) if money else 0,
                         int(land) if land else 0, int(karma) if karma else -99)
            curs = conn.execute('''INSERT or IGNORE into Battles
            (ChatID, ForwarderID, FrwMessageTime, User1ID, User2ID, BattleTime, WinFlag, SendArmy, ReturnArmy, Money, Land, Karma)
            VALUES(?,?,?,
            (SELECT ID FROM GameUser WHERE UserName = ?),
            (SELECT ID FROM GameUser WHERE UserName = ?),
            ?,?,?,?,?,?,?)''',
                         (msg.chat.id, msg.from_user.id, msg.date,
                          user_name1, user_name2,
                          msg.forward_date, 1 if win_flag else 2, int(send_army),
                          int(return_army) if return_army else 0, int(money) if money else 0,
                          int(land) if land else None, int(karma) if karma else None))
            if curs.rowcount == 1:
                str_fwd_time = strftime('%d.%m %H:%M:%S', gmtime(msg.forward_date))
                logger.info('New battle:%s `%s` VS `%s` (@`%s`)', str_fwd_time, user_name1, user_name2, msg.from_user.username)
                return True
            else:
                logger.debug('Battle info already exist')
                return False
    except sqlite3.IntegrityError:
        str_fwd_time = strftime('%d.%m %H:%M:%S', gmtime(msg.forward_date))
        logger.warning('Ошибка добавления записи Battle: %s `%s` VS `%s` (@`%s`)', str_fwd_time, user_name1, user_name2, msg.from_user.username)
        return False


def get_user_battle_stat(user):
    try:
        with sqlite3.connect(SQLITE_DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            logger.debug("SELECT Battles.*,GU1.UserName AS UserName1, GU2.UserName AS UserName2 "
                         "FROM (Battles JOIN GameUser AS GU1 ON User1ID = GU1.ID) JOIN GameUser as GU2 ON User2ID = GU2.ID "
                         "WHERE UserName1='%s' OR UserName2='%s' "
                         "ORDER BY BattleTime DESC LIMIT 6", user, user)
            curs = conn.cursor()
            curs.execute('''SELECT Battles.*,GU1.UserName AS UserName1, GU2.UserName AS UserName2
            FROM (Battles JOIN GameUser AS GU1 ON User1ID = GU1.ID) JOIN GameUser as GU2 ON User2ID = GU2.ID
            WHERE UserName1=? OR UserName2=?
            ORDER BY BattleTime DESC LIMIT 5''', (user, user))
            return curs.fetchall()
    except sqlite3.Error:
        logger.warning('Database error')
        return None

