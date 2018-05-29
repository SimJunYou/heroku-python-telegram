########################################
#          INITIALISATION
#     IMPORTS LOGS AND VARIABLES
#       shortcuts: initvars
########################################

#phone push test 4

import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Global state constants
ROLE, NAME, TOTAL, CURRENT, SICK, STATUS, NOTPRESENT, ADD, END, AI_NOTPRESENT = range(10)
AM_ROLE, AM_NAME, AM_TOTAL, AM_INFO, AM_END = range(5)

# Global variables
def init_vars():
    global psInfo, amInfo, aiNP_count, amAdd_count, endComplete
    psInfo = {'role': '', 'name': '', 'total': '', 'current': '', 'sick': '', 'status': '', 'notpresent': '', 'add': ''}
    amInfo = {'role': '', 'name': '', 'total': ''}
    aiNP_count, amAdd_count = 0, 0
    endComplete = False











########################################
#          PARADE STATE
#        TELEGRAM COMMANDS
#         shortcut: PScomm
########################################

def start(bot, update):
    init_vars() #initialise all global variables
    
    logger.info("User %s initiates report generation", update.message.from_user.first_name)
    
    reply_keyboard = [['/ParadeState'], ['/AdditionalMovement']]
    update.message.reply_text(
        '*Report Generator*\n'
        '============================\n\n'
        'Send /cancel to stop generating.\n\n'
        'Press parade state or additional movement to to continue.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        parse_mode = ParseMode.MARKDOWN)
    

def role(bot, update):
    logger.info("User %s selects Parade State generation", update.message.from_user.first_name)
    reply_keyboard = [['MOD', 'Div IC']]

    update.message.reply_text(
        '*Parade State Generation*\n'
        '============================\n\n'
        'Are you the MOD or Div IC?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        parse_mode = ParseMode.MARKDOWN)

    return NAME

def name(bot, update):
    psInfo['role'] = update.message.text
    update.message.reply_text(
        'Type your name and division i.e. MID Stanley Kor Guanghao (T)',
        reply_markup=ReplyKeyboardRemove())
    return TOTAL
    
def total(bot, update):
    # Checks for division name
    if psInfo["role"] == "Div IC":
        if update.message.text[-3:] == "(T)":
            psInfo["role"] = "Tiger Division IC"
        elif update.message.text[-3:] == "(D)":
            psInfo["role"] = "Dragon Division IC"
        elif update.message.text[-3:] == "(W)":
            psInfo["role"] = "Wolf Division IC"
        else:
            abort(bot, update, "Unclear division name")
            return NAME
        
    psInfo['name'] = update.message.text
    update.message.reply_text('Total strength:')

    return CURRENT

def current(bot, update):
    if update.message.text == "0":
        psInfo['total'] = "Nil"
    elif not update.message.text.isnumeric():
        abort(bot, update, "Non-numerical number for total strength.")
        return TOTAL
    else:
        psInfo['total'] = update.message.text
        
    update.message.reply_text('Current strength:')

    return SICK

def sick(bot, update):
    if update.message.text == "0":
        psInfo['current'] = "Nil"
    elif not update.message.text.isnumeric():
        abort(bot, update, "Non-numerical number for current strength.")
        return CURRENT
    else:
        psInfo['current'] = update.message.text
        
    update.message.reply_text('Number of sick people:')

    return STATUS

def status(bot, update):
    if update.message.text == "0":
        psInfo['sick'] = "Nil"
    elif not update.message.text.isnumeric():
        abort(bot, update, "Non-numerical number of sick people.")
        return SICK
    else:
        psInfo['sick'] = update.message.text
        
    update.message.reply_text('People on status:')

    return NOTPRESENT

def notpresent(bot, update):
    if update.message.text == "0":
        psInfo['status'] = "Nil"
    elif not update.message.text.isnumeric():
        abort(bot, update, "Non-numerical number of people on status.")
        return STATUS
    else:
        psInfo['status'] = update.message.text
        
    update.message.reply_text('Not present:')

    return ADD

def add(bot, update):
    if update.message.text == "0":
        psInfo['notpresent'] = "Nil"
    elif not update.message.text.isnumeric():
        abort(bot, update, "Non-numerical number for people not present.")
        return NOTPRESENT
    else:
        psInfo['notpresent'] = update.message.text
        
    update.message.reply_text('Additional movement (number):')
    
    return END

def end(bot, update):
    global endComplete
    if not endComplete:
        if update.message.text == "0":
            psInfo['add'] = "Nil"
        elif not update.message.text.isnumeric():
            abort(bot, update, "Non-numerical number for additional movement/information.")
            return ADD
        else:
            psInfo['add'] = update.message.text

    endComplete = True

    # Sliding into other conversation states for additional info
    # for other sections like Sick, Status and Not Present

    if psInfo['notpresent'].isnumeric():
        reply_keyboard = [['Continue']]
        update.message.reply_text(
            '*Additional Information*: Not Present\n'
            'Press to continue',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
            parse_mode = ParseMode.MARKDOWN)
        return AI_NOTPRESENT


    
    finalReport = generateParadeState(bot, update)
    if finalReport == False:
        return ROLE
    else:
        update.message.reply_text(finalReport)
    
    return ConversationHandler.END


########################################
#          EXTRA PS INFO
#        TELEGRAM COMMANDS
#         shortcut: PSextra
########################################

def aiNotPresent(bot, update):
    global aiNP_count
    if update.message.text == 'Shore Leave':
        aiNP_count += 1 #for the bullet points

        psInfo['notpresent'] += ("\n\n{}. _ from _ Division ".format(aiNP_count)+
                                "of the 84th MIDS/21st MDEC 1 are currently "+
                                "on shore leave. Shore leave will expire at "+
                                "_H _ 18.")

        update.message.reply_text(
            'Added: Shore Leave'
        )
            
    elif update.message.text == 'Outstation':
        aiNP_count += 1

        psInfo['notpresent'] += ('\n\n{}. _ of '.format(aiNP_count)+
                                'the 84th MIDS/21st MDEC 1 are '+
                                'outstationed for _ at _.')

        update.message.reply_text(
            'Added: Outstation'
        )
            
    elif update.message.text == 'Other':
        aiNP_count += 1

        psInfo['notpresent'] += '\n\n{}.'.format(aiNP_count)

        update.message.reply_text(
            'Added: Other reason'
        )
        
    elif update.message.text == 'End':
        reply_keyboard = [['Continue']]
        update.message.reply_text(
            '*Additional Information*: Not Present\n'
            'Addition of bullet points complete.\n'
            'Press to continue.',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
            parse_mode = ParseMode.MARKDOWN)
        
        return END
    
    logger.info("User {} is adding {} for Parade State (Not Present)".format(update.message.from_user.first_name, update.message.text))

    reply_keyboard = [['Shore Leave', 'Outstation'], ['Other', 'End']]

    update.message.reply_text(
        '*Additional information*: Not Present\n'
        'Choose one to add one bullet point.\n'
        'This menu will come up again unless you choose End.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        parse_mode = ParseMode.MARKDOWN)

    return AI_NOTPRESENT

########################################
#        ADDITIONAL MOVEMENT
#         TELEGRAM COMMANDS
#         shortcuts: AMcomm
########################################

def AM_role(bot, update):
    logger.info("User %s selects Parade State generation", update.message.from_user.first_name)
    reply_keyboard = [['MOD', 'Div IC']]

    update.message.reply_text(
        '*Additional Movement Report Generation*\n'
        '============================\n\n'
        'Are you the MOD or Div IC?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        parse_mode = ParseMode.MARKDOWN)

    return AM_NAME

def AM_name(bot, update):
    amInfo['role'] = update.message.text
    update.message.reply_text(
        'Type your name and division i.e. MID Stanley Kor Guanghao (T)',
        reply_markup=ReplyKeyboardRemove())
    return AM_TOTAL

def AM_total(bot, update):
    # Checks for division name
    if amInfo["role"] == "Div IC":
        if update.message.text[-3:] == "(T)":
            amInfo["role"] = "Tiger Division IC"
        elif update.message.text[-3:] == "(D)":
            amInfo["role"] = "Dragon Division IC"
        elif update.message.text[-3:] == "(W)":
            amInfo["role"] = "Wolf Division IC"
        else:
            abort(bot, update, "Unclear division name")
            return AM_NAME
        
    amInfo['name'] = update.message.text
        
    update.message.reply_text('Total items:')

    return AM_INFO

def AM_info(bot, update):
    global endComplete, amAdd_count
    
    if not endComplete:
        if update.message.text == "0":
            amInfo['total'] = "Nil"
        elif not update.message.text.isnumeric():
            abort(bot, update, "Non-numerical number for total items.")
            return AM_TOTAL
        else:
            amInfo['total'] = update.message.text
    endComplete = True
        
    if update.message.text == 'Securing':
        amAdd_count += 1 #for the bullet points

        amInfo['total'] += ("\n\n{}. ".format(amAdd_count)+
                                "The following midshipmen of the "+
                                "84th MIDS/21st MDEC 1 have been secured "+
                                "at _H _ 18 by _.\n\n"+
                                "a.")

        update.message.reply_text(
            'Added: Securing'
        )
            
    elif update.message.text == 'QM Duties':
        amAdd_count += 1

        amInfo['total'] += ('\n\n{}. '.format(amAdd_count)+
                            'The following midshipmen of the '+
                            '84th MIDS/21st MDEC 1 are at wingline '+
                            'performing QM duties from _H _ 18 to _H _ 18.\n\n'+
                            'a.')

        update.message.reply_text(
            'Added: QM Duties'
        )
            
    elif update.message.text == 'Reaching':
        amAdd_count += 1

        amInfo['total'] += ('\n\n{}. '.format(amAdd_count)+
                            '_ of the 84th MIDS/21st MDEC 1 '+
                            '_ reached wingline as of _H _ 18.')

        update.message.reply_text(
            'Added: Reached a place'
        )

    elif update.message.text == 'Leaving':
        amAdd_count += 1

        amInfo['total'] += ('\n\n{}. '.format(amAdd_count)+
                            '_ of the 84th MIDS/21st MDEC 1 '+
                            '_ left _ for _ as of _H _ 18.')

        update.message.reply_text(
            'Added: Left a place'
        )

    elif update.message.text == 'Other':
        amAdd_count += 1

        amInfo['total'] += ('\n\n{}. '.format(amAdd_count))

        update.message.reply_text(
            'Added: Other'
        )
        
    elif update.message.text == 'End':
        reply_keyboard = [['Continue']]
        update.message.reply_text(
            '*Additional Movement/Information:*\n'
            'Addition of bullet points complete.\n'
            'Press to continue.',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
            parse_mode = ParseMode.MARKDOWN)
        
        return AM_END
    
    logger.info("User {} is adding {} for Additional Movement/Information".format(update.message.from_user.first_name, update.message.text))
    reply_keyboard = [['QM Duties', 'Securing', 'Other'], ['Leaving', 'Reaching', 'End']]

    update.message.reply_text(
        '*Additional Movement/Information:*\n'
        'Choose one to add one bullet point.\n'
        'This menu will come up again unless you choose End.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        parse_mode = ParseMode.MARKDOWN)

    return AM_INFO

def AM_end(bot, update):
    finalReport = generateAddMoveReport(bot, update)
    update.message.reply_text(finalReport)

    logger.info("Add. Movement Report delivered")
    
    return ConversationHandler.END

########################################
#              EXTERNAL
#              COMMANDS
#         shortcut: EXcomms
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
#         shortcut: genreport
########################################

def generateParadeState(bot, update):
    logger.info("User %s completed generation of Parade State", update.message.from_user.first_name)
    
    timePeriod = getTimePeriod()
    timeGroup = getTimeGroup()

    #Parade state generation      
    report = """Good {}, Sirs.\n
I am {}, {} of the 84th MIDS/21st MDEC 1. The {} parade state for {} is as follows:\n
Total strength: {}\n
Present strength: {}\n
Reporting sick: {}\n
Medical status: {}\n
Not present: {}\n
Additional movement/information: {}\n
For your information, Sirs.
    
    """.format(timePeriod, psInfo["name"], psInfo["role"], timePeriod, timeGroup,
               psInfo["total"], psInfo["current"],psInfo["sick"], psInfo["status"],
               psInfo["notpresent"], psInfo["add"])

    return report

def generateAddMoveReport(bot, update):
    logger.info("User %s completed generation of Additional Movement Report", update.message.from_user.first_name)

    timePeriod = getTimePeriod()
    timeGroup = getTimeGroup()

    #Parade state generation      
    report = """Good {}, Sirs.\n
I am {}, {} of the 84th MIDS/21st MDEC 1.\n
Additional movement/information: {}\n
For your information, Sirs.
    """.format(timePeriod, amInfo["name"], amInfo["role"], amInfo["total"])

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
    update.message.reply_text(
        'Press continue',
        reply_markup=ReplyKeyboardMarkup([['Continue']], one_time_keyboard=True))

def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


########################################
#               M A I N
#           F U N C T I O N
########################################

def main():
    # Start updater
    updater = Updater("241346491:AAH09_cf9KfaFohGgXUo96ljvOeyqcD1k4o")
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    # Add conversation handler for parade state
    pState_handler = ConversationHandler(
        entry_points=[CommandHandler('ParadeState', role)],

        states={
            ROLE: [MessageHandler(Filters.text, role)],
            NAME: [MessageHandler(Filters.text, name)],
            TOTAL: [MessageHandler(Filters.text, total)],
            CURRENT: [MessageHandler(Filters.text, current)],
            SICK: [MessageHandler(Filters.text, sick)],
            STATUS: [MessageHandler(Filters.text, status)],
            NOTPRESENT: [MessageHandler(Filters.text, notpresent)],
            ADD: [MessageHandler(Filters.text, add)],
            AI_NOTPRESENT: [MessageHandler(Filters.text, aiNotPresent)],
            END: [MessageHandler(Filters.text, end)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(pState_handler)

    # Add conversation handler for additional movement report
    addMovement_handler = ConversationHandler(
        entry_points=[CommandHandler('AdditionalMovement', AM_role)],

        states={
            AM_ROLE: [MessageHandler(Filters.text, AM_role)],
            AM_NAME: [MessageHandler(Filters.text, AM_name)],
            AM_TOTAL: [MessageHandler(Filters.text, AM_total)],
            AM_INFO: [MessageHandler(Filters.text, AM_info)],
            AM_END: [MessageHandler(Filters.text, AM_end)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(addMovement_handler)
            
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    logger.info("Now running")
    

if __name__ == '__main__':
    main()
