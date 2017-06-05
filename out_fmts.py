from time import strftime, gmtime
from tools import str_human_int


def battle_stat_fmt(db_data):
    result_list = []
    for row in db_data:
        str_fwd_time = strftime('%d.%m %H:%M:%S', gmtime(row['BattleTime']))
        if row['WinFlag'] == 1:
            money = str_human_int(row['Money']) + '💰'
            if row['Land']:
                user1 = '🏆 {} 🗡'.format(row['UserName1'])
                user2 = '🛡 {}'.format(row['UserName2'])
                land = '{}🗺'.format(str_human_int(row['Land']))
            else:
                user1 = '🏆 {} 🛡'.format(row['UserName1'])
                user2 = '🗡 {}'.format(row['UserName2'])
                land = ''
        else:
            money = '-' + str_human_int(row['Money']) + '💰'
            if row['Land']:
                user1 = '{} 🛡'.format(row['UserName1'])
                user2 = '🗡 {} 🏆'.format(row['UserName2'])
                land = '-{}🗺'.format(str_human_int(row['Land']))
            else:
                user1 = '{} 🗡'.format(row['UserName1'])
                user2 = '🛡 {} 🏆'.format(row['UserName2'])
                land = ''
        army = '{}/{}⚔'.format(row['ReturnArmy'], row['SendArmy'])

        result_list.append('{}\n'
                           '*{:<12}* `{:>12}`\n'
                           '{:<12} {:>7} {:>7}\n\n'
                           .format(str_fwd_time,
                                   user1, user2,
                                   army, money, land))
    # logger.debug(''.join(result_msg))
    return ''.join(result_list)


def global_stat_fmt(db_data):
    if db_data and db_data['Total'] > 0:
        return '''Статистика по игроку `{}` из `{}`

Всего сражений: {}
Побед/поражений: {}👍/ {}👎

Отправлено/потеряно войск: {} / -{} ⚔

Затраты на отправку/обучение/итого армии:
    -{} / -{} / *-{}* 💰

Заработано/проиграно/итого денег:
    {} / -{} / *{}* 💰

Завоевано/потеряно/итого земель:
    {} / -{} / *{}* 🗺

Суммарная прибыль  от войны с учетом всех затрат: *{}* 💰
'''.format(db_data['UserName'], db_data['LandName'],
           db_data['Total'], db_data['Wins'], db_data['Losts'],
           str_human_int(db_data['SendArm']), str_human_int(db_data['LostArm']),
           str_human_int(db_data['SendArmCost']), str_human_int(db_data['LostArmCost']),
           str_human_int(db_data['TotalArmCost']),
           str_human_int(db_data['WinMoney']), str_human_int(db_data['LostMoney']),
           str_human_int(db_data['TotalMoney']),
           str_human_int(db_data['WinLand']), str_human_int(db_data['LostLand']), str_human_int(db_data['TotalLand']),
           str_human_int(db_data['TotalProfit']))
    else: return 'Совпадений не найдено'


def whois_info_fmt(db_data):
    if not db_data: return 'Совпадений не найдено'
    result_list = ['Найдено *{}* совпадений:\n\n'.format(len(db_data))]
    for row in db_data[:5]:
        if row['PlayerID']: player = '`{}` из {}'.format(row['PlayerName'],
                                                         '`{}`'.format(row['LandName']) if row['LandName'] else '???')
        else: player = '???'
        if row['TlgrUserID']: user = '`{}` `{}` (@`{}`)'.format(row['FirstName'],
                                                                row['LastName'] if row['LastName'] else '',
                                                                row['TlgUsername'] if row['TlgUsername'] else '')
        else: user = '@???'
        result_list.append('{}\n{}\n\n'.format(player, user))
    return ''.join(result_list)

