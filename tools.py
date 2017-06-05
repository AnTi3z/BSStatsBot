def str_human_int (x):
    if abs(x) < 10000: return '%d' % x
    i = 0
    while abs(round(x)) >= 1000 and i < 3:
        x /= 1000
        i += 1
    suffix = ['','k','M','G'][i]

    if abs(round(x)) >= 100 or suffix == '': return '{:.0f}{}'.format(x,suffix)
    elif abs(round(x)) >= 10: return '{:.1f}{}'.format(x,suffix)
    else: return '{:.2f}{}'.format(x,suffix)


def get_acc_lvl(chat_id):
    IngressersID = -1001096635324
    JPV_ID = -1001096024584
    PisyaID = -203826152
    if chat_id == IngressersID: return 100
    elif chat_id == JPV_ID  or chat_id == PisyaID: return 10
    return 0
