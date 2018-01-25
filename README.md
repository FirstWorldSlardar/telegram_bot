Telegram Bot using Python Wrapper

**Installation :**

- Install the dependencies with a `pip install -r requirements.txt`
- Create a secret.key file at the root with the secret Key of your bot in it
- Create a file named "sqlite.db" at the root
- Start your bot with `python main.py`

**Bot Commands:**
- /setUp <currency> <value_limit> : the bot will tell you when the currency rise up the value_limit
- /setDown <currency> <value_limit>: the bot will tell you when the currency falls down the value_limit
- /clearLimits <currency>/<> : without argument it clears all the previously set up limits
- /seeLimits : show you all limits set

- /setValues <currency> <number_tokens> : the bot will remember you own <number_tokens> of <currency>
- /seeValues : generate a pie charts of all your holdings.
- /clearValues <currency> : clear the nomber of tokens you set previously with the <currency>
