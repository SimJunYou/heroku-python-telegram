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

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
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
    logger.info("User %s initiates report generation", update.message.from_user.first_name)
    
    reply_keyboard = [['Parade State'|'/pState'], ['Additional Movement'|'/aMovement']]
    update.message.reply_text(
        '*Report Generator*\n\n'
        'Send /cancel to stop generating.\n\n'
        'Press parade state or additional movement to to continue.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        parse_mode = ParseMode.MARKDOWN)

def pState(bot, update):
    logger.info("User %s selects Parade State generation")
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

    finalReport = generateParadeState(bot, update)
    if finalReport == False:
        return ROLE
    else:
        update.message.reply_text(finalReport)
    
    return ConversationHandler.END

########################################
#              EXTERNAL
#              COMMANDS
########################################

from datetime import datetime
from pytz import timezone
DTG = "%d%H%MH %b %y"
hour = "%H"
singaporeTime = datetime.now(timezone("Asia/Singapore"))

def getTimeGroup():
    return singaporeTime.strftime(DTG)

def getTimePeriod():
    currentHour = int(singaporeTime.strftime(hour))
    if currentHour < 11:
        return "morning"
    elif currentHour < 18:
        return "afternoon"
    else:
        return "evening"


########################################
#           INFO COLLATING
#          REPORT GENERATION
########################################

def generateParadeState(bot, update):
    logger.info("User %s completed generation", update.message.from_user.first_name)
    
    timePeriod = getTimePeriod()
    timeGroup = getTimeGroup()

    # Checks for division name
    if info["role"] == "Div IC":
        if info["name"][-3:] == "(T)":
            info["role"] = "Tiger Division IC"
        elif info["name"][-3:] == "(D)":
            info["role"] = "Dragon Division IC"
        elif info["name"][-3:] == "(W)":
            info["role"] = "Wolf Division IC"
        else:
            abort(bot, update, "Unclear division name")
            return False

    #Checks for valid number of people
    for each in ("sick", "status", "notpresent", "add"):
        if info[each] == "Nil":
            pass
        elif info[each].isnumeric():
            for i in range(int(info[each])):
                info[each] += "\n\n{}.".format(i+1)
        else:
            print(info[each], each)
            abort(bot, update, "Non-numerical number of people for "+each)
            return False

      #Parade state generation      
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

def abort(bot, update, error):
    user = update.message.from_user
    logger.info("User %s caused an error!", user.first_name)
    logger.info("Error: "+error)
    
    update.message.reply_text("Abort! Your information is flawed, please revise what you sent.")
    update.message.reply_text("Specific error: "+error)
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

    dp.add_handler(CommandHandler("start", start))

    # Add conversation handler for parade state
    pState_handler = ConversationHandler(
        entry_points=[CommandHandler('pState', pState)],

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

    dp.add_handler(pState_handler)

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
