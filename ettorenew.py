import logging
import random
import json
import os
import re
import time
import telegram
import telegram.ext
from threading import Timer,Thread,Event
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from datetime import datetime


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

random.seed(datetime.now())

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard_interact = [['Food', 'Drink'],
                          ['Fun', 'Stats'],
		          ['Done']]
markup_interact = ReplyKeyboardMarkup(reply_keyboard_interact, one_time_keyboard=True)

reply_keyboard_food = [['Croccantini', 'Bistecca']]
markup_food = ReplyKeyboardMarkup(reply_keyboard_food, one_time_keyboard=True)

reply_keyboard_drink = [['Acqua', 'Pepsi']]
markup_drink = ReplyKeyboardMarkup(reply_keyboard_drink, one_time_keyboard=True)

reply_keyboard_fun = [['Carezze', 'Giretto']]
markup_fun = ReplyKeyboardMarkup(reply_keyboard_fun, one_time_keyboard=True)

class perpetualTimer():

	def __init__(self,t,hFunction):
		self.t=t
		self.hFunction = hFunction
		self.thread = Timer(self.t,self.handle_function)

	def handle_function(self):
		self.hFunction()
		self.thread = Timer(self.t,self.handle_function)
		self.thread.start()

	def start(self):
		self.thread.start()

	def cancel(self):
		self.thread.cancel()

def decrease():
	for file in os.listdir("ettori/"):
		chat_id = re.split("[-.]",file)[-0]
		#print (str(chat_id) + "-data.json")
		r = open('ettori/' + str(chat_id) + "-data.json", "r")
		load = json.load(r)
		food = load["ettore"][0]["food"]
		load["ettore"][0]["food"] = str(float(food) - 2)
		drink = load["ettore"][0]["drink"]
		load["ettore"][0]["food"] = str(float(drink) - 2)
		drink = load["ettore"][0]["fun"]
		load["ettore"][0]["fun"] = str(float(fun) - 2)
		r.close()
		w = open('ettori/' + str(chat_id) + "-data.json", "w")
		json.dump(load, w)
		w.close()
		#if float(load["ettore"][0]["food"]) < 5:
		#	messages.send_message(chat_id = chat_id, text = "Ettore ha fame.")
	print ('a')
	return main
#Da modificare dopo per creare il file relativo all'Ettore dello User
def facts_to_str(user_data):
	facts = list()

	for key, value in user_data.items():
		facts.append('{} - {}'.format(key, value))

	return "\n".join(facts).join(['\n', '\n'])

def start(update, context):
	chat_id = update.message.chat.id
	if os.path.isfile('ettori/' + str(chat_id) + "-data.json"):
		update.message.reply_text("Ricordati di dare da mangiare, da bere e far divertire Lola almeno una volta al giorno. Ma non esagerare!")
		return main
		#print('a')
	else:
		f = open('ettori/' + str(chat_id) + "-data.json", "w+")
		data = {}
		birth = time.time()
		data['ettore'] = []
		data['ettore'].append({
    		'food': '5',
		'drink': '5',
		'fun': '5',
		'time': str(birth)
		})
		json.dump(data, f)
		
		#f = open('ettori/' + str(chat_id) + "-data.json")
		#load = json.load(f)
		#print (load["ettore"][0]["food"])
		url = 'https://i.ibb.co/Ry59bmC/P-20150623-103022-HDR-removebg-preview.png'
		update.message.reply_text("Benvenuto in Lola, il tuo pupper viruale. Questa e\' Lola:")
		update.message.reply_photo(photo = url)
		update.message.reply_text("Dovrai prenderti cura di lei, altrimenti scappera\' o morira\'. Puoi farlo attraverso il menu\' /Interact. Ricordati di dare da mangiare, da bere e far divertire Lola almeno una volta al giorno. Ma non esagerare!")
		return main
	#return chat_id

def interact(update, context):
	chat_id = update.message.chat.id
	r = open('ettori/' + str(chat_id) + "-data.json", "r")
	load = json.load(r)
	food = load["ettore"][0]["food"]
	drink = load["ettore"][0]["drink"]
	fun = load["ettore"][0]["fun"]
	if float(food) < 0 or float(drink) < 0 or float(fun) < 0:
		update.message.reply_text("Hai dedicato troppe poche attenzioni a Lola! Dall'ultima volta che ti sei connesso Lola e\' morta.")
		update.message.reply_photo(photo = 'https://i.ibb.co/0C524Lm/lolded.png')
		days = (time.time() - float(load["ettore"][0]["time"])) / 86400
		update.message.reply_text("La tua Lola ha vissuto {} giorni".format(days))
		os.remove('ettori/' + str(chat_id) + "-data.json")
		return main
	elif float(food) > 10 or float(drink) > 10 or float(fun) > 10:
		#update.message.reply_text("Lola e\' scappata!")
		#update.message.reply_photo(photo = 'https://serving.photos.photobox.com/60029026823275f6385942e9eb7c45d37613925d52dcec0e059d8408bf993c50b51a4156.jpg')
		days = (time.time() - float(load["ettore"][0]["time"])) / 86400
		update.message.reply_text("La tua Lola e\' stata con te {} giorni".format(days))
		os.remove('ettori/' + str(chat_id) + "-data.json")
		return main
	else:
		update.message.reply_text("Cosa vuoi fare con Lola?",reply_markup=markup_interact)
	return CHOOSING

def check(value):
	if value < 0:
		reply = 'troppo poco, e\' morta!'
	if value >= 0 and value <= 3:
		reply = 'pochissimo, e\' ad un livello critico.'
	if value > 3 and value < 8:
		reply = 'quanto basta, e\' soddisfatta.'
	if value >= 8 and value < 10:
		reply = 'un po\' troppo, attenzione.'
	if value >= 10:
		reply = 'troppo. Lola non capisce piu\' niente ed e\' scappata! Premi /interact per vedere quanto tempo e\' stata con te.'
	return reply
def regular_choice(update, context):
	chat_id = update.message.chat.id
	r = open('ettori/' + str(chat_id) + "-data.json", "r")
	load = json.load(r)
	food = load["ettore"][0]["food"]
	drink = load["ettore"][0]["drink"]
	fun = load["ettore"][0]["fun"]
	text = update.message.text
	context.user_data['choice'] = text
	if text == 'Food':
		update.message.reply_text('Cosa vuoi dare da mangiare a Lola?',reply_markup=markup_food)
		return CHOOSING
	if text == 'Drink':
		update.message.reply_text('Cosa vuoi dare da bere a Lola?',reply_markup=markup_drink)
		return CHOOSING
	if text == 'Fun':
		update.message.reply_text('Cosa vuoi far fare a Lola?',reply_markup=markup_fun)
		return CHOOSING
	if text == 'Stats':
		update.message.reply_text('Ecco le stats di Lola:')
		hunger, thirst, fun_lev = 'A', 'b', 'c'
		if float(food) > 0 and float(food) < 3:
			hunger = 'alto'
		if float(food) >= 3 and float(food) < 8:
			hunger = 'normale'
		if float(food) > 8 and float(food) <= 10:
			hunger = 'basso'

		if float(drink) > 0 and float(drink) < 3:
			thirst = 'alto'
		if float(drink) >= 3 and float(drink) < 8:
			thirst = 'normale'
		if float(drink) > 8 and float(drink) < 10:
			thirst = 'basso'

		if float(fun) > 0 and float(fun) < 3:
			fun_lev = 'basso'
		if float(fun) >= 3 and float(fun) < 8:
			fun_lev = 'normale'
		if float(fun) > 8 and float(fun) <= 10:
			fun_lev = 'alto'

		update.message.reply_text('Livello fame : {} \n'.format(hunger) + 'Livello sete : {}\n'.format(thirst) + 'Livello divertimento : {}'.format(fun_lev) )
		return ConversationHandler.END
	if text == 'Croccantini':
		ran = random.uniform(0,2)
		w = open('ettori/' + str(chat_id) + "-data.json", "w")
		load["ettore"][0]["food"] = str(ran + float(food))
		json.dump(load, w)
		w.close()
		reply = check(float(load["ettore"][0]["food"]))
		update.message.reply_text('Lola ha mangiato {}'.format(reply))
    		return ConversationHandler.END
	if text == 'Bistecca':
		ran = random.uniform(0,5)
		w = open('ettori/' + str(chat_id) + "-data.json", "w")
		load["ettore"][0]["food"] = str(ran + float(food))
		json.dump(load, w)
		w.close()
		reply = check(float(load["ettore"][0]["food"]))
		update.message.reply_text('Lola ha mangiato {}'.format(reply))
    		return ConversationHandler.END
	if text == 'Acqua':
		ran = random.uniform(0,1.5)
		w = open('ettori/' + str(chat_id) + "-data.json", "w")
		load["ettore"][0]["drink"] = str(ran + float(drink))
		json.dump(load, w)
		w.close()
		reply = check(float(load["ettore"][0]["drink"]))
		update.message.reply_text('Lola ha bevuto {}'.format(reply))
    		return ConversationHandler.END
	if text == 'Pepsi':
		ran = random.uniform(0,3)
		w = open('ettori/' + str(chat_id) + "-data.json", "w")
		load["ettore"][0]["drink"] = str(ran + float(drink))
		json.dump(load, w)
		w.close()
		reply = check(float(load["ettore"][0]["drink"]))
		update.message.reply_text('Lola ha bevuto {}'.format(reply))
    		return ConversationHandler.END
	if text == 'Carezze':
		ran = random.uniform(0,1.5)
		w = open('ettori/' + str(chat_id) + "-data.json", "w")
		load["ettore"][0]["fun"] = str(ran + float(fun))
		json.dump(load, w)
		w.close()
		reply = check(float(load["ettore"][0]["fun"]))
		update.message.reply_text('Lola si e\' divertita {}'.format(reply))
    		return ConversationHandler.END
	if text == 'Giretto':
		ran = random.uniform(0,3)
		w = open('ettori/' + str(chat_id) + "-data.json", "w")
		load["ettore"][0]["fun"] = str(ran + float(fun))
		json.dump(load, w)
		w.close()
		reply = check(float(load["ettore"][0]["fun"]))
		update.message.reply_text('Lola si e\' divertita {}'.format(reply))
    		return ConversationHandler.END
	


def received_information(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text("Hai scelto:{}".format(facts_to_str(user_data)),
                              reply_markup=markup)

    return CHOOSING


def done(update, context):
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
	# Create the Updater and pass it your bot's token.
	# Make sure to set use_context=True to use the new context based callbacks
	# Post version 12 this will no longer be necessary
	

	updater = Updater("1066381965:AAGpw9getXGb61_QcRmXkXSXdyWdisDT15c", use_context=True)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	start_handler = CommandHandler('start', start)
	dp.add_handler(start_handler)

	# Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
	conv_handler = ConversationHandler(
        	entry_points=[CommandHandler('interact', interact)],

        	states={
            	CHOOSING: [MessageHandler(Filters.regex('^(Food|Drink|Fun|Stats)$'),
                                      regular_choice),
                           MessageHandler(Filters.regex('^(Croccantini|Bistecca)$'),
                                      regular_choice),
                           MessageHandler(Filters.regex('^(Acqua|Pepsi)$'),
                                      regular_choice),
                           MessageHandler(Filters.regex('^(Carezze|Giretto)$'),
                                      regular_choice)
				],


			    TYPING_CHOICE: [MessageHandler(Filters.text,
				                           regular_choice)
				            ],

			    TYPING_REPLY: [MessageHandler(Filters.text,
				                       received_information),
				           ],
			},

        	fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    	)

	dp.add_handler(conv_handler)

	# log all errors
	dp.add_error_handler(error)


	t = perpetualTimer(86400, decrease)
	t.start()

	#decrease_food()
	#time.sleep(30.0 - ((time.time() - starttime) % 30.0))

	
	# Start the Bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
    main()

