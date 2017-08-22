import re
import statdb
import logging
from out_fmts import battle_stat_fmt

logger = logging.getLogger('BSstatbot')

trg_regexp = re.compile(r'расположился \U0001f5e1?\U0001f608?(?:\[(.+?)\u200b*\])?(.+) в своих владениях (.+) размером \d+.+За победу ты получишь -?\d+.+')
btl_regexp = re.compile(r'Битва с (?!альянсом )(?:\U0001f5e1)?(?:\U0001f608)?(?:\[(.+?)\u200b*\])?(?P<user_name2>.+) окончена\. (?:(?P<win_flag>Поздравляю)|К сожалению), (?P<user_name1>.+)(?:, твоя|! Твоя).+? (?:Никто из|(?P<return_army>\d+). (?:из|без)) (?P<send_army>\d+)?(?:(?:.+награда составила |.+казна опустела на )(?P<money>\d+))?(?:.+ (?P<land>\d+). отошли (?:к твоим владениям\.|(?P<land_name2>.+)\.))?(?:.+изменилась на (?P<karma>-?\d+))?.*', re.S)
ally_list_regexp = re.compile(r'\[(.+?)\u200b*\](.+) / (\d+) / \U0001f5e1?\U0001f608?(.+)')


def bs_fwd_parser(msg, acc_lvl):
    # Разведка
    trg = trg_regexp.search(msg.text)
    if trg:
        statdb.new_game_user(trg.group(2))
        statdb.update_user_land(trg.group(2), trg.group(3))
        if trg.group(1):
            statdb.new_alliance(trg.group(1))
            statdb.new_user_alliance(trg.group(2), trg.group(1))
        else:
            statdb.delete_user_alliance(trg.group(2))
        result = statdb.get_user_battle_stat(trg.group(2), acc_lvl)
        if result:
            return battle_stat_fmt(result)
        else:
            return

    # Сражение
    btl = btl_regexp.search(msg.text)
    if btl:
        statdb.new_game_user(btl.group('user_name2'))
        statdb.new_game_user(btl.group('user_name1'), msg.from_user.id)
        if not btl.group('win_flag') and btl.group('land_name2'):
            statdb.update_user_land(btl.group('user_name2'), btl.group('land_name2'))
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
