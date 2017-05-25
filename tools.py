def str_human_int (x):
    if x < 10000: return '%d' % x
    i = 0
    while round(x) >= 1000 and i < 3:
        x /= 1000
        i += 1
    suffix = ['','k','M','G'][i]

    if round(x) >= 100 or suffix == '': return '{:.0f}{}'.format(x,suffix)
    elif round(x) >= 10: '{:.1f}{}'.format(x,suffix)
    else: return '{:.2f}{}'.format(x,suffix)
