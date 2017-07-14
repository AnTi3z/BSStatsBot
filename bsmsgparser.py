import re
import statdb
import logging
from out_fmts import battle_stat_fmt
from tools import get_acc_lvl

logger = logging.getLogger('BSstatbot')

ally_list_regexp = re.compile(r'\[(.+?)\u200b?\](.+) / (\d+) / \U0001f5e1?\U0001f608?(.+)')

def bs_fwd_parser(msg):
    # Разведка
    trg = re.search(
        r'расположился \U0001f5e1?\U0001f608?(.+) в своих владениях (.+) размером \d+.+\nЗа победу ты получишь -?\d+.+\n',
        msg.text)
    if trg:
        statdb.new_game_user(trg.group(1))
        statdb.update_user_land(trg.group(1), trg.group(2))
        acc_lvl = get_acc_lvl(msg.chat.id)
        result = statdb.get_user_battle_stat(trg.group(1), acc_lvl)
        if result:
            return battle_stat_fmt(result)
        else:
            return

    # Сражение
    btl = re.search(
        r'Битва с (?P<user_name2>.+) окончена\. (?:(?P<win_flag>Поздравляю)|К сожалению), (?P<user_name1>.+)(?:, твоя|! Твоя).+ (?:Никто из|(?P<return_army>\d+). из) (?P<send_army>\d+)(?:(?:.+с наградой |.+разграблена на )(?P<money>\d+))?(?:.+ (?P<land>\d+). отошли (?:к твоим владениям\.|(?P<land_name2>.+)\.))?(?:.+изменилась на (?P<karma>-?\d+))?.*',
        msg.text)
    if btl:
        statdb.new_game_user(btl.group('user_name2'))
        statdb.new_game_user(btl.group('user_name1'), msg.from_user.id)
        if not btl.group('win_flag'): statdb.update_user_land(btl.group('user_name2'), btl.group('land_name2'))
        statdb.new_battle(msg, **btl.groupdict())
        return

    # Список альянсов
    ally_list = ally_list_regexp.findall(msg.text)
    for ally in ally_list or []:
        statdb.new_game_user(ally[3])
        statdb.new_alliance(ally[0])
        statdb.new_user_alliance(ally[3], ally[0])
        statdb.update_alliance(*ally)
        # print('Альянс: {}, тег: {}, кол-во: {}, лидер: {}'.format(ally[0], ally[1], ally[2], ally[3]))
