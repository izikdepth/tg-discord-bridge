## HOW TO USE
## DISCORD
1. Create a discord bot [HERE](https://discord.com/developers/applications). Once created, navigate to the "Bot" section to create your bot and get the token.
2. Enable "MESSAGE CONTENT INTENT" under the "Bot" settings.
3. Copy the bot token.
4. Create a new discord channel and call it tg bridge.
5. Copy your tg bridge's channel id.

## TELEGRAM
1. Create a bot with [BOT FATHER](https://t.me/BotFather) on telegram.
2. COpy your bot token.
3. Copy your telegram group's id.

## .env
1. Copy the contents of .env.example into .env 
   ```bash
   cp .env.example .env # copy .env.example .env on windows
   ```
2. fill the .env file with your bots' tokens and channel & group id. 

## INSTALL REQUIREMENTS
1. Install python3.10+ 
2. Install dependencies with 
   ```bash
   pip install -r requirements.txt ## pip3 install -r requirements.txt on windows
   ```

## START BOT
1. Start bot with 
   ```bash
   python3 main.py # or python main.py on windows
   ```