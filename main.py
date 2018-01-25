#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters #,InlineQueryHandler
#from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent

from random import randint
from functools import wraps
#from uuid import uuid4
#from telegram.utils.helpers import escape_markdown


# Enable logging
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
                    # level=logging.DEBUG)
logger = logging.getLogger(__name__)

from db_functions import get_from_sql, exec_sql
# functions to request the lite database

### COMMANDS FUNCTIONS ###
def hello(bot, update):
    update.message.reply_text('Hello {}'.format(update.message.from_user.first_name))

def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

def voice(bot, update):
	update.message.reply_text("Tu as la plus belle voix du monde ! 😄\nMais moi aussi, écoute :")
	update.message.reply_voice(update.message.voice)

def alea(bot, update, args):
	#n = int(' '.join(args))
	bot.send_message(chat_id=update.message.chat_id, text=randint(1,int(args[0])))

def rdv(bot, update, args):
	txt = "{0} : _{1}pers._ \n@{2}".format(' '.join(args), "1", update.message.from_user.username)
	# on crée un nouveau message
	result_msg = bot.send_message(chat_id=update.message.chat_id, text=txt, parse_mode="Markdown")
	# on récupère son id
	id_message = result_msg.message_id
	# on enregistre cet id dans la db
	exec_sql('INSERT OR REPLACE INTO rdvs VALUES (%d, %d, "%s")' % (update.message.chat_id, id_message, result_msg.text))
	# on delete le message initial
	bot.deleteMessage(chat_id=update.message.chat_id, message_id=update.message.message_id)
	# on pin le message que l'on vient créer
	bot.pinChatMessage(chat_id=update.message.chat_id, message_id=id_message, disable_notification=True)


def setUp(bot, update, args):
	if len(args)<2:
		return None
	currency_name, limit = args[0], float(args[1])
	exec_sql('INSERT INTO cryptos VALUES(%d, "%s", "%s", %.3g)' % (update.message.chat_id, "up", currency_name, limit))
	bot.send_message(
		chat_id=update.message.chat_id, 
		text="""
		Quand la valeur du %s dépassera $%.3g, vous en serez averti.
		""" 
		% (currency_name, limit) 
	)


def setDown(bot, update, args):
	if len(args)<2:
		return None
	currency_name, limit = args[0], float(args[1])
	exec_sql(
		'INSERT INTO cryptos VALUES(%d, "%s", "%s", %.3g)'
		% (update.message.chat_id, "down", currency_name, limit)
	)
	bot.send_message(
		chat_id=update.message.chat_id, 
		text="""
		Quand la valeur du %s tombera sous $%.3g, vous en serez averti.
		""" 
		% (currency_name, limit) 
	)

def clearLimits(bot, update, args=None):
	if args:
		# Delete the one crypto specified
		currency_name = args[0]
		exec_sql(
			'DELETE FROM cryptos WHERE id_chat=%d AND currency="%s"' 
			% (update.message.chat_id, currency_name)
		)
		bot.send_message(
			chat_id=update.message.chat_id,
			text="Les limites sur %s ont été supprimées." % (currency_name,)
		)
	else:
		# Delete all crypto being watched
		exec_sql('DELETE FROM cryptos WHERE id_chat=%d' % (update.message.chat_id,))
		bot.send_message(
			chat_id=update.message.chat_id,
			text="Toutes vos limites ont été supprimées."
		)

def seeLimits(bot, update, args=None):
	if args:
		# Delete the one crypto specified
		currency_name = args[0]
		results = get_from_sql(
			'SELECT type, value FROM cryptos WHERE id_chat=%d AND currency="%s"' 
			% (update.message.chat_id, currency_name)
		)
		txt = "Les limites dans ce chat pour le %s sont :\n" % currency_name
		for result in results:
			type_limit, value = result
			txt += """
			%s : $%.3g \n
			""" % (type_limit, value)
		bot.send_message(
			chat_id=update.message.chat_id,
			text=txt
		)
	else:
		# Delete all crypto being watched
		results = get_from_sql(
			'SELECT type, currency, value FROM cryptos WHERE id_chat=%d' 
			% (update.message.chat_id,)
		)
		txt = "Les limites dans ce chat sont :\n"
		for result in results:
			type_limit, currency, value = result
			txt += """
			%s -> %s : $%.3g \n
			""" % (currency, type_limit, value)
		bot.send_message(
			chat_id=update.message.chat_id,
			text=txt
		)



def delete_pin_msg(bot, update):
	bot.deleteMessage(chat_id=update.message.chat_id, message_id=update.message.message_id)

def unpin(bot, update):
	bot.unpinChatMessage(chat_id=update.message.chat_id)


def plus_un(bot, update):
	if update.message.text =="+1":
		# on récupère le chat_id de la discussion en cours
		chat_id = update.message.chat_id
		requete = '''
			SELECT 	id_message, txt
			FROM    rdvs
			WHERE   id_chat = %d
			AND 	id_message = (SELECT MAX(id_message) FROM rdvs WHERE id_chat = %d)
		''' % (chat_id,chat_id)
		# on récupère dans la db le message_id pinned and le txt correspondant
		message_id = get_from_sql(requete)[0][0]
		txt = get_from_sql(requete)[0][1]
		# on édite le message
		splitted_text = txt.split('\n')
		n_pers = len(splitted_text)
		# le nombre de personne qui ont fait '+1' (len(splitted)-1) +1 pour celui-ci.

		n_txt = ":".join(splitted_text[0].split(':')[:-1]).strip(' ') +" : _%dpers._ " % (n_pers,) 
		# First ligne, we make sure entering à ":" isn't a problem
		# and that the format defined precedently is respected
		for username in splitted_text[1:]:
			n_txt += '\n' + username 

		n_txt += '\n@'+update.message.from_user.username
		bot.editMessageText(chat_id=chat_id, message_id=message_id, text=n_txt, parse_mode="Markdown")
		# on parse en Markdown pour pouvoir ajouter des italiques par exemple
		# on actualise la db avec le txt édité
		requete = '''
			UPDATE 	rdvs
			SET 	txt = "%s"
			WHERE	id_chat = %d
			AND 	id_message = %d
		''' % (n_txt,chat_id,message_id)
		exec_sql(requete)
###


### HELPER FUNCTIONS ###

#def edit(bot, chat_id, message_id, txt):
#	bot.editMessageText(chat_id=chat_id, message_id=message_id, text="Texte édité.")

###

# def restricted(func):
#     @wraps(func)
#     def wrapped(bot, update, *args, **kwargs):
#         user_id = update.effective_user.id
#         if user_id not in LIST_OF_ADMINS:
#             print("Unauthorized access denied for {}.".format(user_id))
#             return
#         return func(bot, update, *args, **kwargs)
#     return wrapped

'''
# def echo(bot, update):
#     """Echo the user message."""
#     update.message.reply_text(update.message.text)
    

def inlinequery(bot, update):
    """Handle the inline query."""
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Caps",
            input_message_content=InputTextMessageContent(
                query.upper())),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Bold",
            input_message_content=InputTextMessageContent(
                "*{}*".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Italic",
            input_message_content=InputTextMessageContent(
                "_{}_".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN)),
        ]
    update.inline_query.answer(results)
'''

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)



def setup():
	print("Démarrage du bot")


def main():
	"""Run bot."""

	# Get the bot secret key 
	f_key = open("secret.key", "r")
	secret_key = f_key.readline().strip(' ')
	updater = Updater(token=secret_key)

	# periodically check the cryptos
	from cryptos import check_cryptos
	jobQueue = updater.job_queue
	job_check_cryptos = jobQueue.run_repeating(
		check_cryptos,
		interval=15,
		first=0
	)


	dispatcher = updater.dispatcher
	# on different commands - answer in Telegram
	dispatcher.add_handler(CommandHandler("hello", hello))
	dispatcher.add_handler(CommandHandler("start", start))
	dispatcher.add_handler(CommandHandler("rdv", rdv, pass_args=True))
	dispatcher.add_handler(CommandHandler("unpin", unpin))
	dispatcher.add_handler(CommandHandler("alea", alea, pass_args=True))
	dispatcher.add_handler(CommandHandler("setUp", setUp, pass_args=True))
	dispatcher.add_handler(CommandHandler("setDown", setDown, pass_args=True))
	dispatcher.add_handler(CommandHandler("clearLimits", clearLimits, pass_args=True))
	dispatcher.add_handler(CommandHandler("seeLimits", seeLimits, pass_args=True))
	dispatcher.add_handler(MessageHandler(Filters.text, plus_un))

	# Ne fonctionne pas car le bot ne listen pas ses propres messages envoyés...
	# dispatcher.add_handler(MessageHandler(Filters.status_update.pinned_message & Filters.chat(username="@iloveraffa_bot"), delete_pin_msg))
	
	# on noncommand i.e message - echo the message on Telegram
	# dispatcher.add_handler(MessageHandler(Filters.text, echo))
	# dispatcher.add_handler(MessageHandler(Filters.voice, voice))

	# dispatcher.add_handler(InlineQueryHandler(inlinequery))

	


	# log all errors
	dispatcher.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
	# SIGABRT. This should be used most of the time, since start_polling() is
	# non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__=="__main__":
	setup()
	main()