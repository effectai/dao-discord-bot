from tinydb import Query


def cool_number(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0

    ft = '%.{}f%s'.format(1 if magnitude >= 2 else 0)
    return ft % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])


def get_account_name_from_context(db, ctx, account_name):
    if account_name and '<' not in account_name:
        return account_name

    discord_id = ctx.message.author.id
    if ctx.message.mentions:
        discord_id = ctx.message.mentions[0].id

    if discord_id:
        User = Query()
        user = db.search(User.discord_id == discord_id)
        if user:
            return user[0]['account_name']

    return None
