import telegram
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import logging

from string_constants import TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telegram.Bot(TOKEN)

MENU, USER_TYPES_NEW, USER_SEARCH_QUERY = range(3)

KEYBOARD = [
                ['✍ New Note', '👀 Search'],
                ['🗒 List of Notes']
            ]

static_markup = ReplyKeyboardMarkup(KEYBOARD,
                                    one_time_keyboard=True,
                                    resize_keyboard=True)


def create_inline_menu(options, update):
    # List of tuples to list of lists, turning the datetime into more comprehensive and short format
    options = [list(element) for element in options]
    for index in range(len(options)):
        dt = options[index][-1]
        dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        options[index][-1] = str(dt.strftime('%d.%m %H:%M'))

    # Creates the keyboard of options, passing datetime and update_id into callback_data
    inline_keyboard = [InlineKeyboardButton(dt + ' ' + text, callback_data=dt + ' ' + str(update_id))
                       for update_id, text, dt in options]

    # Every option has its own row for better UI
    inline_keyboard = [[element] for element in inline_keyboard]

    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    update.message.reply_text('Please choose one of the options:', reply_markup=reply_markup)
