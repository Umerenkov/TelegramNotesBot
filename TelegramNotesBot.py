from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
import sqlite3
import logging
import os

# Bot token
TOKEN = '#########:########################'

# Proxy settings for things to work in Russia
'''
REQUEST_KWARGS = {
    'proxy_url': 'socks5://142.93.232.142:####',
    'urllib3_proxy_kwargs': {
        'username': '##########',
        'password': '##########',
    }
}
'''

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
bot = telegram.Bot(TOKEN)

help_message = '''This bot is intended for collecting and storing notes for your needs. \n
Click *\"✍ New Note\"* button to take a new note, \n
Click *\"👀 Show\"* button to view a particular note,
You will be asked any part of the needed note or the date or time of its creation. \n
Click *\"🗒 List of Notes\"* button to view the list of taken notes. \n
Enter */help* command to view this message again. \n'''


def start(update, context):
    # Send a message when the command /start is issued.
    bot.send_message(chat_id=update.message.chat_id,
                     text='*Greetings, traveler!* \n' + help_message, parse_mode=telegram.ParseMode.MARKDOWN)

    keyboard = [[InlineKeyboardButton("✍ New Note", callback_data='/take_note'),
                 InlineKeyboardButton("👀 Show", callback_data='/show')],
                [InlineKeyboardButton("🗒 List of Notes", callback_data='/notes_list')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose one of the options:', reply_markup=reply_markup)

    # Creates a brand new database file in case of absebse of any .db files in current folder
    if not os.path.exists(os.path.dirname(__file__) + '/*.db'):
        with open('database.db', 'w'):
            pass


def callbackHandler(bot, update, chat_data):
    callbackquery = update.callback_query
    print(callbackquery)
    querydata = callbackquery.data
    print(querydata)
    '''
    if not 'lang' in  chat_data:
        getChatFile(chat_data, update.message.chat.id)
        if not 'lang' in chat_data:
            chat_data['lang'] = ""
    if not querydata:
        return
    '''

def help(update, context):
    # Send the help message when the command /help is issued.
    bot.send_message(chat_id=update.message.chat_id,
                     text=help_message, parse_mode=telegram.ParseMode.MARKDOWN)


def take_note(update, context):
    # Writing a new note into the database.
    update.message.reply_text('Please write the body of the new note: ')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS Notes (Body text, Datetime text)')
    cur.execute('INSERT INTO Notes VALUES (?, ?)', (update.message.text, update.message.date))
    conn.commit()
    conn.close()

    update.message.reply_text('✅ Your note has been succesfully taken.')

def notes_list(update, context):
    # Returns a list of taken notes
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM Notes')
    notes = cur.fetchall()
    conn.close()

    # Stripping the first lines of notes and printing them with some formatting and corresponding dates
    notes = [(note[:note.find('\n')].strip() + '...' if len(note) > 60 else note, date) for note, date in notes]
    for note, date in notes:
        update.message.reply_text(date + '\n *' + note.ljust(60) + '*' + '\t \t \n')


def show(update, context):
    # Show the particular note
    update.message.reply_text('Please write any part of the needed note or the date or time of its creation: \n'
                              'for example: "do not forget to turn off the iron", "16:20" or "05.01.2009"')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM Notes')
    notes = cur.fetchall()
    conn.close()

    query = update.message.text

    # Selecting candidates that contain entered query
    candidates = [note for note in notes if (note[0].find(query) != -1 or note[1].find(query) != -1)]

    if not candidates:
        # if empty
        update.message.reply_text('Sorry, we couldn\'t find such note! \n'
                                  'Press *\"List of Notes\"* button to get valid options.')

    elif len(candidates) == 1:
        # if there's the one, print a date and the note itself.
        update.message.reply_text(candidates[0][1] + '\n *' + candidates[0][0].ljust(60) + '*' + '\t \t \n')

    else:
        # if there's >1 of them, Print a number of candidate, date and the note itself.
        # Numbering of candidates starts from 1
        for index in range(len(candidates)):
            _note = candidates[index][0]
            _date = candidates[index][1]
            update.message.reply_text(_date + '\n *' + str(index + 1) + '. ' +
                                      (_note[:_note.find('\n')].strip() + '...' if len(_note) > 60 else _note).ljust(
                                          60) + '*' + '\t \t \n')

        update.message.reply_text('Please choose one of the options, printing out its number: ')
        query = update.message.text

        # Filtering everything except digits to show a note under entered index
        index = int(''.join(filter(lambda x: x.isdigit(), query))) - 1

        if index not in range(len(candidates)):
            update.message.reply_text('Sorry, we couldn\'t find such note! \n'
                                      'Press *\"List of Notes\"* button to get valid options.')
        else:
            update.message.reply_text(candidates[index][1] + '\n *' + str(index + 1) + '. ' +
                                      candidates[index][0].ljust(60) + '*' + '\t \t \n')


def error(update, context):
    # Log Errors caused by Updates.
    logger.warning('Update %s caused error %s', update, context.error)


def unknown(update, context):
    # Send a message when the command /help is issued.
    update.message.reply_text('Sorry, I didn\'t understand that command!')


def main():
    # Start the bot.
    # Create the EventHandler and get the dispatcher to register handlers
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))

    dp.add_handler(CallbackQueryHandler(callbackHandler))
    dp.add_handler(CommandHandler('take_note', take_note))
    dp.add_handler(CommandHandler('notes_list', notes_list))
    dp.add_handler(CommandHandler('show', show))

    '''
    # menu
    button_list = [
        telegram.InlineKeyboardButton('col1', callback_data=...),
        telegram.InlineKeyboardButton('col2', callback_data=...),
        telegram.InlineKeyboardButton('row 2', callback_data=...) 
        # callback_data: str – Optional. 
        # Data to be sent in a callback query to the bot when button is pressed, 1-64 bytes.
    ]
    reply_markup = telegram.InlineKeyboardMarkup(util.build_menu(button_list, n_cols=2))
    bot.send_message(..., 'A two-column menu', reply_markup=reply_markup)
    '''

    # log all errors
    dp.add_error_handler(error)

    # processing unknown messages and commands
    dp.add_handler(MessageHandler(Filters.text & Filters.command, unknown))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
