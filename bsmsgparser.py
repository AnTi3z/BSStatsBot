import re
import statdb
import logging
from time import strftime, gmtime
from tools import str_human_int

logger = logging.getLogger('BSstatbot')

def bs_fwd_parser(msg):
    # Разведка
    trg = re.search(
        r'расположился \U0001f5e1?\U0001f608?(.+) в своих владениях (.+) размером \d+.+\nЗа победу ты получишь -?\d+.+\n',
        msg.text)
    if trg:
        statdb.new_game_user(trg.group(1))
        statdb.update_user_land(trg.group(1), trg.group(2))
        result = statdb.get_user_battle_stat(trg.group(1))
        if result:
            result_msg = []
            for row in result:
                str_fwd_time = strftime('%d.%m %H:%M:%S', gmtime(row['BattleTime']))
                sign = '' if row['WinFlag'] == 1 else '-'
                if row['WinFlag'] == 1:
                    user1 = '🏆 ' + row['UserName1']
                    user2 = row['UserName2']
                    sign = ''
                else:
                    user1 = row['UserName1']
                    user2 = row['UserName2'] + ' 🏆'
                    sign = '-'
                money = sign + str_human_int(row['Money'])
                if row['Land']:
                    land = sign + str_human_int(row['Land'])
                else: land = '0'
                army_ws = max(0,11 - len(str(row['ReturnArmy'])) - len(str(row['SendArmy'])))
                money_ws = max(0, 6 - len(money))
                #land_ws = max(0,6 - len(land))
                result_msg.append('{}\n'
                                  '*{:<12}*{}`{:>12}`\n'
                                  '{}/{}⚔{}{}💰{}{}🗺\n\n'
                                  .format(str_fwd_time,
                                          user1, '  ', user2,
                                          row['ReturnArmy'], row['SendArmy'], ' ' * army_ws,
                                          money, ' ' * money_ws, land))
            #logger.debug(''.join(result_msg))
            return ''.join(result_msg)
        else: return

    #Сражение
    btl = re.search(
        r'Битва с (?P<user_name2>.+) окончена\. (?:(?P<win_flag>Поздравляю)|К сожалению), (?P<user_name1>.+)(?:, твоя|! Твоя).+ (?:Никто из|(?P<return_army>\d+). из) (?P<send_army>\d+)(?:(?:.+с наградой |.+разграблена на )(?P<money>\d+))?(?:.+ (?P<land>\d+). отошли (?:к твоим владениям\.|(?P<land_name2>.+)\.))?(?:.+изменилась на (?P<karma>-?\d+))?.*',
        msg.text)
    if btl:
        statdb.new_game_user(btl.group('user_name2'))
        statdb.new_game_user(btl.group('user_name1'), msg.from_user.id)
        if not btl.group('win_flag'): statdb.update_user_land(btl.group('user_name2'), btl.group('land_name2'))
        statdb.new_battle(msg,**btl.groupdict())
        return
