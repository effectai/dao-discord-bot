def cool_number(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0

    ft = '%.{}f%s'.format(1 if magnitude >= 2 else 0)
    return ft % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
