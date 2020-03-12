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

CHOOSING = range(1)

#setting up the different keyboard interactions
reply_keyboard_interact = [['Food', 'Drink'],
                          ['Fun', 'Stats'],
		          ['Done']]
markup_interact = ReplyKeyboardMarkup(reply_keyboard_interact, one_time_keyboard=True)

reply_keyboard_food = [['Crunches', 'Steak']]
markup_food = ReplyKeyboardMarkup(reply_keyboard_food, one_time_keyboard=True)

reply_keyboard_drink = [['Water', 'Lemonade']]
markup_drink = ReplyKeyboardMarkup(reply_keyboard_drink, one_time_keyboard=True)

reply_keyboard_fun = [['Snuggling', 'Go for a walk']]
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

#function that decreases vital signs every 24 hours
def decrease():
	for file in os.listdir("puppies/"):
		chat_id = re.split("[-.]",file)[-0]
		#print (str(chat_id) + "-data.json")
		r = open('puppies/' + str(chat_id) + "-data.json", "r")
		load = json.load(r)
		food = load["puppy"][0]["food"]
		load["puppy"][0]["food"] = str(float(food) - 2)
		drink = load["puppy"][0]["drink"]
		load["puppy"][0]["food"] = str(float(drink) - 2)
		drink = load["puppy"][0]["fun"]
		load["puppy"][0]["fun"] = str(float(fun) - 2)
		r.close()
		w = open('puppies/' + str(chat_id) + "-data.json", "w")
		json.dump(load, w)
		w.close()
	return main

def start(update, context):
	chat_id = update.message.chat.id
	if os.path.isfile('puppies/' + str(chat_id) + "-data.json"):
		update.message.reply_text("Remember to feed and play with your puppy, but don't overdo it!")
		return main

	else:
		f = open('puppies/' + str(chat_id) + "-data.json", "w+")
		data = {}
		birth = time.time()
		data['puppy'] = []
		data['puppy'].append({
    		'food': '5',
		'drink': '5',
		'fun': '5',
		'time': str(birth)
		})
		json.dump(data, f)
		#set an url with a pic of a puppy
		url = 'https://i.ibb.co/Ry59bmC/P-20150623-103022-HDR-removebg-preview.png'
		update.message.reply_text("Welcome, this is your puppy")
		update.message.reply_photo(photo = url)
		update.message.reply_text("You'll have to take car of her, you can do it via /interact. Remember to feed her and play with her, but don't overdo it!")
		return main
	#return chat_id

def interact(update, context):
	chat_id = update.message.chat.id
	r = open('puppies/' + str(chat_id) + "-data.json", "r")
	load = json.load(r)
	food = load["puppy"][0]["food"]
	drink = load["puppy"][0]["drink"]
	fun = load["puppy"][0]["fun"]
	if float(food) < 0 or float(drink) < 0 or float(fun) < 0:
		update.message.reply_text("You haven't taken enough care of your puppy, she died since last time!")
		update.message.reply_photo(photo = 'https://i.ibb.co/0C524Lm/lolded.png')
		days = (time.time() - float(load["puppy"][0]["time"])) / 86400
		update.message.reply_text("Your puppy lived for {} days".format(days))
		os.remove('puppies/' + str(chat_id) + "-data.json")
		return main
	elif float(food) > 10 or float(drink) > 10 or float(fun) > 10:
		#update.message.reply_text("Lola e\' scappata!")
		#update.message.reply_photo(photo = 'https://serving.photos.photobox.com/60029026823275f6385942e9eb7c45d37613925d52dcec0e059d8408bf993c50b51a4156.jpg')
		days = (time.time() - float(load["puppy"][0]["time"])) / 86400
		update.message.reply_text("Your puppy stayed with you for {} days".format(days))
		os.remove('puppies/' + str(chat_id) + "-data.json")
		return main
	else:
		update.message.reply_text("What do you want to do with your puppy?",reply_markup=markup_interact)
	return CHOOSING
#check 'checks' for fun, thirst and hunger values after you interact with her and gives a response to the user
def check(value):
	if value < 0:
		reply = 'not enough, she died!'
	if value >= 0 and value <= 3:
		reply = 'very little, she is at a critical level.'
	if value > 3 and value < 8:
		reply = 'enough, she is satisfied.'
	if value >= 8 and value < 10:
		reply = 'A bit too much, watch out.'
	if value >= 10:
		reply = 'too much she is confused and she is running away! Press /interact to see how much time she stayed with you.'
	return reply
#regular_choice manages your decisions and their outcomes
def regular_choice(update, context):
	chat_id = update.message.chat.id
	r = open('puppies/' + str(chat_id) + "-data.json", "r")
	load = json.load(r)
	food = load["puppy"][0]["food"]
	drink = load["puppy"][0]["drink"]
	fun = load["puppy"][0]["fun"]
	text = update.message.text
	context.user_data['choice'] = text
	if text == 'Food':
		update.message.reply_text('What do you want to feed her?',reply_markup=markup_food)
		return CHOOSING
	if text == 'Drink':
		update.message.reply_text('What do you want dive her to drink?',reply_markup=markup_drink)
		return CHOOSING
	if text == 'Fun':
		update.message.reply_text('What activities do you want to do with her?',reply_markup=markup_fun)
		return CHOOSING
	if text == 'Stats':
		update.message.reply_text('Here are her stats:')
		hunger, thirst, fun_lev = 'A', 'b', 'c'
		if float(food) > 0 and float(food) < 3:
			hunger = 'high'
		if float(food) >= 3 and float(food) < 8:
			hunger = 'average'
		if float(food) > 8 and float(food) <= 10:
			hunger = 'low'

		if float(drink) > 0 and float(drink) < 3:
			thirst = 'high'
		if float(drink) >= 3 and float(drink) < 8:
			thirst = 'average'
		if float(drink) > 8 and float(drink) < 10:
			thirst = 'low'

		if float(fun) > 0 and float(fun) < 3:
			fun_lev = 'low'
		if float(fun) >= 3 and float(fun) < 8:
			fun_lev = 'average'
		if float(fun) > 8 and float(fun) <= 10:
			fun_lev = 'high'

		update.message.reply_text('Hunger level : {} \n'.format(hunger) + 'Thirst level : {}\n'.format(thirst) + 'Fun level : {}'.format(fun_lev) )
		return ConversationHandler.END
	if text == 'Crunchies':
		ran = random.uniform(0,2)
		w = open('puppies/' + str(chat_id) + "-data.json", "w")
		load["puppy"][0]["food"] = str(ran + float(food))
		json.dump(load, w)
		w.close()
		reply = check(float(load["puppy"][0]["food"]))
		update.message.reply_text('She ate {}'.format(reply))
    		return ConversationHandler.END
	if text == 'Steak':
		ran = random.uniform(0,5)
		w = open('puppies/' + str(chat_id) + "-data.json", "w")
		load["puppy"][0]["food"] = str(ran + float(food))
		json.dump(load, w)
		w.close()
		reply = check(float(load["puppy"][0]["food"]))
		update.message.reply_text('She ate {}'.format(reply))
    		return ConversationHandler.END
	if text == 'Water':
		ran = random.uniform(0,1.5)
		w = open('puppies/' + str(chat_id) + "-data.json", "w")
		load["puppy"][0]["drink"] = str(ran + float(drink))
		json.dump(load, w)
		w.close()
		reply = check(float(load["puppy"][0]["drink"]))
		update.message.reply_text('She drank {}'.format(reply))
    		return ConversationHandler.END
	if text == 'Lemonade':
		ran = random.uniform(0,3)
		w = open('puppies/' + str(chat_id) + "-data.json", "w")
		load["puppy"][0]["drink"] = str(ran + float(drink))
		json.dump(load, w)
		w.close()
		reply = check(float(load["puppy"][0]["drink"]))
		update.message.reply_text('She drank {}'.format(reply))
    		return ConversationHandler.END
	if text == 'Snuggling':
		ran = random.uniform(0,1.5)
		w = open('puppies/' + str(chat_id) + "-data.json", "w")
		load["puppy"][0]["fun"] = str(ran + float(fun))
		json.dump(load, w)
		w.close()
		reply = check(float(load["puppy"][0]["fun"]))
		update.message.reply_text('She enjoed herself {}'.format(reply))
    		return ConversationHandler.END
	if text == 'Go for a walk':
		ran = random.uniform(0,3)
		w = open('puppies/' + str(chat_id) + "-data.json", "w")
		load["puppy"][0]["fun"] = str(ran + float(fun))
		json.dump(load, w)
		w.close()
		reply = check(float(load["puppy"][0]["fun"]))
		update.message.reply_text('She enjoed herself {}'.format(reply))
    		return ConversationHandler.END
	

def done(update, context):
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
	# Create the Updater and pass it your bot's token.
	# Make sure to set use_context=True to use the new context based callbacks
	# Post version 12 this will no longer be necessary
	

	updater = Updater("TOKEN", use_context=True)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	start_handler = CommandHandler('start', start)
	dp.add_handler(start_handler)

	# Add conversation handler with the states CHOOSING
	conv_handler = ConversationHandler(
        	entry_points=[CommandHandler('interact', interact)],

        	states={
            	CHOOSING: [MessageHandler(Filters.regex('^(Food|Drink|Fun|Stats)$'),
                                      regular_choice),
                           MessageHandler(Filters.regex('^(Crunchies|Steak)$'),
                                      regular_choice),
                           MessageHandler(Filters.regex('^(Water|Lemonade)$'),
                                      regular_choice),
                           MessageHandler(Filters.regex('^(Snuggling|Go for a walk)$'),
                                      regular_choice)
				],
			},

        	fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    	)

	dp.add_handler(conv_handler)

	# log all errors
	dp.add_error_handler(error)


	t = perpetualTimer(86400, decrease)
	t.start()

	
	# Start the Bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
    main()

