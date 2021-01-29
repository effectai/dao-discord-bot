## 🤖 Effect DAO Discord Bot
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/effectai/dao-discord-bot/issues)

The Effect DAO Discord bot is being used to connect discord accounts to EOS blockchain account.
It will set the Discord role corresponding to your DAO rank.

The bot is restricted to talk in the #bot-spam channel or DM only. 
Verification can only be done through DM.

➡️ <b><a href="https://discord.gg/hM3237cYXP">Join the Effect DAO Discord!</a></b>

#### Features 🦾
- Verify your EOS account through DM
- `!unlink` your EOS account
- `!update` your Effect DAO stats
- `!dao` view a user's DAO stats 

#### Running the bot
The bot creates a `db.json` file, make sure this file is persistent. 
Make sure the environment variable `DISCORD_BOT_TOKEN` is set to your token.
Install the requirements and run `run.py`.

```bash
# Or run it with Docker
docker-compose up -d --build
```

#### Troubleshooting
If you have issues you can create an issue in this repo, or <a href="https://discord.gg/hM3237cYXP">join us on Discord</a>. 
If you encounter issues with connecting to the Discord API make sure your token environment variable is set correctly. 
If you have issues with the TinyDB location, change the location of the database file in `run.py`.