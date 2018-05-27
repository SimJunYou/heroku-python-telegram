#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ROLE, NAME, TOTAL, CURRENT, SICK, STATUS, NOTPRESENT, ADD, END = range(9)
info = {'role': '', 'name': '', 'total': '', 'current': '', 'sick': '', 'status': '', 'notpresent': '', 'add': ''}

########################################
#          GETTING INFO
#        TELEGRAM COMMANDS
########################################

def start(bot, update):
    reply_keyboard = [['Continue']]
    update.message.reply_text(
        'Parade State Generator\n\n'
        'Send /cancel to stop generating.\n\n'
        'Press continue',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ROLE

def role(bot, update):
    reply_keyboard = [['MOD', 'Div IC']]

    update.message.reply_text(
        'Are you the MOD or Div IC?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return NAME

def name(bot, update):
    info['role'] = update.message.text
    update.message.reply_text('Type your name and division i.e. MID Stanley Kor Guanghao (T)',
                              reply_markup=ReplyKeyboardRemove())
    return TOTAL
    
def total(bot, update):
    info['name'] = update.message.text
    update.message.reply_text('Total strength:')

    return CURRENT

def current(bot, update):
    if update.message.text == "0":
        info['total'] = "Nil"
    else:
        info['total'] = update.message.text
    update.message.reply_text('Current strength:')

    return SICK

def sick(bot, update):
    if update.message.text == "0":
        info['current'] = "Nil"
    else:
        info['current'] = update.message.text
    update.message.reply_text('Number of sick people:')

    return STATUS

def status(bot, update):
    if update.message.text == "0":
        info['sick'] = "Nil"
    else:
        info['sick'] = update.message.text
    update.message.reply_text('People on status:')

    return NOTPRESENT

def notpresent(bot, update):
    if update.message.text == "0":
        info['status'] = "Nil"
    else:
        info['status'] = update.message.text
    update.message.reply_text('Not present:')

    return ADD

def add(bot, update):
    if update.message.text == "0":
        info['notpresent'] = "Nil"
    else:
        info['notpresent'] = update.message.text
    update.message.reply_text('Additional movement (number):')
    
    return END

def end(bot, update):
    if update.message.text == "0":
        info['add'] = "Nil"
    else:
        info['add'] = update.message.text

    finalReport = generateReport(bot, update)
    if finalReport == False:
        return ROLE
    else:
        update.message.reply_text(finalReport)
    
    return ConversationHandler.END

########################################
#              EXTERNAL
#              COMMANDS
########################################

from time import localtime, strftime

def getTimeGroup():
    return strftime("%d%H%MH %b %y", localtime())

def getTimePeriod():
    hour = int(strftime("%H", localtime()))
    if hour < 11:
        return "morning"
    elif hour < 18:
        return "afternoon"
    else:
        return "evening"


########################################
#           INFO COLLATING
#          REPORT GENERATION
########################################



def generateReport(bot, update):
    timePeriod = getTimePeriod()
    timeGroup = getTimeGroup()

    if info["role"] == "Div IC":
        if info["name"][-3:] == "(T)":
            info["role"] = "Tiger Division IC"
        elif info["name"][-3:] == "(D)":
            info["role"] = "Dragon Division IC"
        elif info["name"][-3:] == "(W)":
            info["role"] = "Wolf Division IC"
        else:
            abort(bot, update)
            return False
            
    report = """Good {}, Sirs.\n
I am {}, {} of the 84th MIDS, 21st MDEC 1. The {} parade state for {} is as follows:\n
Total strength: {}\n
Present strength: {}\n
Reporting sick: {}\n
Medical status: {}\n
Not present: {}\n
Additional movement/information: {}\n
For your information, Sirs.
    
    """.format(timePeriod, info["name"], info["role"], timePeriod, timeGroup,
               info["total"], info["current"],info["sick"], info["status"],
               info["notpresent"], info["add"])

    return report

########################################
#           UTILITY COMMANDS
#             DO NOT TOUCH
########################################

def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Report Generation Cancelled',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def abort(bot, update):
    update.message.reply_text("Abort! Your information is flawed, please revise what you sent.")
    update.message.reply_text("Type anything to begin from entering your appointment again.")
   
def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


########################################
#               M A I N
#           F U N C T I O N
########################################

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("241346491:AAH09_cf9KfaFohGgXUo96ljvOeyqcD1k4o")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ROLE: [MessageHandler(Filters.text, role)],
            NAME: [MessageHandler(Filters.text, name)],
            TOTAL: [MessageHandler(Filters.text, total)],
            CURRENT: [MessageHandler(Filters.text, current)],
            SICK: [MessageHandler(Filters.text, sick)],
            STATUS: [MessageHandler(Filters.text, status)],
            NOTPRESENT: [MessageHandler(Filters.text, notpresent)],
            ADD: [MessageHandler(Filters.text, add)],
            END: [MessageHandler(Filters.text, end)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    

if __name__ == '__main__':
    main()
