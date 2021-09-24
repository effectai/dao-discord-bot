## 🤖 Effect DAO Discord Bot
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/effectai/dao-discord-bot/issues) ![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/effectai/dao-discord-bot)

➡️ <b><a href="https://discord.gg/hM3237cYXP">Join the Effect DAO Discord!</a></b>

### Features 🦾
The Effect DAO Discord bot is being used to connect discord accounts to EOS blockchain account.
It can also show DAO account details, Proposals overviews and details of proposals.
Furthermore, it can show you the following reminders:
- when the voting duration is almost ending
- when a proposal gets created
- when a cycle gets created 
- when the weekly DAO call is happening.

The bot is restricted to talk in the #bot-spam channel or DM only. 
Verification can only be done through DM.

The bot needs the following permissions to run appropiately.
![Screenshot from 2021-09-24 12-03-24](https://user-images.githubusercontent.com/24189525/134658560-a769e4df-dd4d-42ee-972b-03932e85c88e.png)

#### Proposals
- `!proposals list` List of active/pending proposals.
- `!proposals find <id>` Retrieve the proposal with the given id and then show the details of it.
- `!proposals create_channel <id>` With the given id, retrieve the proposal and show it's details on the freshly created text channel.

> NOTE: the `!proposals create_channel` command can only be used by members who are part of the EFFECT.AI Team.

#### DAO
- `!dao account <account_name>` Retrieve details of the DAO account, if no account_name given, it will retrieve the details of the account that is linked to the discord user.
- `!dao update <account_name>` Update the account_name that is connected to your Discord account.
- `!dao unlink` Unlink the current DAO account.

#### Cycle
- `!cycle` Show cycle details such as what the current cycle is, when the cycle started, how long it takes until it ends and when the voting duration ends.

#### Reminders
There are a couple of reminders that the bot runs:
- `dao_call_notify` is a **cron** notifier which runs every wednesday 5 PM (UTC +02:00) because of the weekly DAO call.
- `dao_vote_notify` is a **date** notifier which runs on a specific date, for this notifier it runs on the date 1 day prior before that the vote_duration ends.
- `dao_new_cycle_notify` is an **interval** notifier which runs after an amount of time. Now it runs after 1 hour, repeatedly.
- `dao_new_proposals_notify` is an **interval** is an **interval** notifier which runs after an amount of time. Now it runs after 1 hour, repeatedly.

With the following command you can reschedule the time of a notifier:
- `!reschedule <trigger> <job_id> <args>`

Based on the `trigger`, you will have to pass different arguments (`args`).

- `cron`
- `date`
- `interval`

with `cron`, you can only pass the day_of_week, hour and minute. For example. `!reschedule cron dao_call_notify wednesday 15 10`

with `date`, you can onlly pass a datetime, which is in the following format, `YYYY-MM-DD HH:mm:ssZ` (`1970-01-01 01:02:03+00:00`)

with `interval` you can only pass arguments in the following order; weeks, days, hours, minutes and seconds. For example, `!reschedule interval dao_new_cycle_notify 0 0 1 0 0` which translates to `0 weeks, 0 days, 1 hour, 0 minutes, 0 seconds` so that means the notifier will run after 1 hour repeatedly.

> NOTE: The `!reschedule` command can only be used by members of the Effect.AI team.

#### Other commands
- `!ping` Pong!

### Running the bot
The bot creates a `db.json` file, make sure this file is persistent. 
Make sure the environment variable `DISCORD_BOT_TOKEN` is set to your token.
Also make sure if you running the bot in your own local discord server, to change the default variable ids to the one of your server.
Install the requirements and run `run.py`.

```bash
# Or run it with Docker
docker-compose up -d --build
```

### Troubleshooting
If you have issues you can create an issue in this repo, or <a href="https://discord.gg/hM3237cYXP">join us on Discord</a>. 
If you encounter issues with connecting to the Discord API make sure your token environment variable is set correctly. 
If you have issues with the TinyDB location, change the location of the database file in `run.py`.
