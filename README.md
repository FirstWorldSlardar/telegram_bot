## Telegram Bot using Python Wrapper (python-telegram-bot) ##

**Installation :**

1. Install conda (Anaconda)
2. Create a conda env from file:
  ```bash
  conda env create -f env.yaml
  ```
3. Create a secret.key file at the root with the secret Key of your bot in it
4. Create a file named "sqlite.db" at the root
5. Start your bot with:
  ```bash
  $ ./bot.sh
  ```

**
To update the env.yaml, just launch command:
$ ./save_env.sh

**Conda useful commands**

Search package infos:
  ```bash
  $ conda search packagename
  ```
indicate the version and the build of the package if found.

Install a package in a env:
  ```bash
  $ source activate envname
  $ conda install packagename[=version][=build]
  ```

**Bot Commands:**

*Everyday commands*
- /alea $int : random int between 0 and $int
- /rdv $place_and_date: if bot is admin (can delete message), delete the
poster's message and create its own with $place_and_date and the poster
username on it.
- +1 : after a /rdv command, add the poster's username to the pinned message.
- /hello: dumb command

*Crypto monitoring*
- /setUp $currency $valuelimit : the bot will tell you when the currency rise up the valuelimit
- /setDown $currency $valuelimit: the bot will tell you when the currency falls down the valuelimit
- /clearLimits $currency : without argument it clears all the previously set up limits
- /seeLimits : show you all limits set

- /setValues $currency $numbertokens : the bot will remember you own numbertokens of currency
- /seeValues : generate a pie charts of all your holdings.
- /clearValues $currency : clear the nomber of tokens you set previously with the <currency>
