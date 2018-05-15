Telegram Bot using Python Wrapper

**Installation :**

1. Install conda
2. Create a conda env from fil:
3. conda env create -f env.yaml
4. Create a secret.key file at the root with the secret Key of your bot in it
5. Create a file named "sqlite.db" at the root
6. Start your bot with:
  ```bash
  $ ./bot.sh
  ```


To update the env.yaml, just launch command:
$ ./save_env.sh

**Conda useful commands**

Search package infos:
$ conda search packagename
-> may indicate the version and the build.

Install a package in a env:
$ source activate envname
$ conda install packagename[=version][=build]


**Bot Commands:**

- /setUp $currency $valuelimit : the bot will tell you when the currency rise up the valuelimit
- /setDown $currency $valuelimit: the bot will tell you when the currency falls down the valuelimit
- /clearLimits $currency : without argument it clears all the previously set up limits
- /seeLimits : show you all limits set

- /setValues $currency $numbertokens : the bot will remember you own numbertokens of currency
- /seeValues : generate a pie charts of all your holdings.
- /clearValues $currency : clear the nomber of tokens you set previously with the <currency>
