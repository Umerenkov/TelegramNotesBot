from telegram.ext import Updater, CommandHandler, ConversationHandler, Filters, MessageHandler, CallbackQueryHandler

from service_functions import *
from string_constants import *
from database_interactions import *
from regexps import *


def start(update, context):
    # Sends a message when the command /start is issued, refers to the user by name and surname or by username
    if update.message.chat.first_name and update.message.chat.last_name:
        name = '*{} {}!* \n'.format(update.message.chat.first_name, update.message.chat.last_name)
    else:
        name = '*{}!* \n'.format(update.message.chat.username)
    text = GREETING + name + HELP_MESSAGE
    update.message.reply_markdown(text=text, reply_markup=static_markup)
    # create_db() if it's needed to

    return MENU


def take_note(update, context):
    # Reaction on pressing the 'Take Note' button
    update.message.reply_markdown(text=PLEASE_WRITE_NEW)

    return USER_TYPES_NEW


def write_new(update, context):
    # Collects the update data from user and storing it into the database
    update_id, user_id = update.update_id, update.message.chat.id
    text, datetime = update.message.text, update.message.date
    # Pushes the collected data
    insert_update(update_id, user_id, text, datetime)
    update.message.reply_markdown(text=SUCCESS, reply_markup=static_markup, quote=True)

    return MENU


def notes_list(update, context):
    # Reaction on pressing the 'List of Notes' button
    user_id = update.message.chat.id
    options = get_notes_by_user_id(user_id)
    if options:
        # Creates a menu of notes belonging to this user
        create_inline_menu(options, update)
    else:
        update.message.reply_markdown(text=PLEASE_CREATE_FIRSTLY, reply_markup=static_markup)
        return MENU


def button(update, context):
    # Reaction on pressing the option button from inline menu
    query = update.callback_query
    date, time, update_id = query.data.split(' ')
    query.edit_message_text(text="*Note dated {} at {}:*".format(date, time),
                            parse_mode=telegram.ParseMode.MARKDOWN)

    # Gets the body of the note by an update_id passed in callback_data, returns text
    text = get_note_by_update_id(update_id)
    update.callback_query.message.reply_markdown(text=text, reply_markup=static_markup)

    return MENU


def search(update, context):
    # Reaction on pressing the 'Search' button
    update.message.reply_markdown(text=SEARCH_RESPONSE)

    return USER_SEARCH_QUERY


def search_query(update, context):
    # Handles the entered query
    user_id = update.message.chat.id
    text = update.message.text

    # Collects all notes of particular user from the database
    options = get_notes_by_user_id(user_id)

    # List of tuples to list of lists, turning the datetime into more comprehensive format
    options = [list(element) for element in options]
    for index in range(len(options)):
        dt = options[index][-1]
        dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        options[index][-1] = str(dt.strftime('%d.%m.%Y %H:%M:%S'))

    # Declares the set of final regex matches. Stores update_ids
    matching_set = set()

    # Recognizes entered time by regex and adds matches to a set
    if re.search(time_pattern, text):
        time_cut = re.search(time_pattern, text).group(0)
        for option in options:
            if time_cut in option[-1]:
                matching_set.add(option[0])

    # Recognizes entered date by regex and adds matches to a set
    if re.search(date_pattern, text):
        date_cut = re.search(date_pattern, text).group(0)
        for option in options:
            if date_cut in option[-1]:
                matching_set.add(option[0])

    # Purges the text from punctuation and creates a regex for text recognition
    text_pattern = create_text_regex(text)

    # Recognizes entered text by regex and adds matches to a set
    for option in options:
        if re.match(text_pattern, option[1]) is not None:
            matching_set.add(option[0])

    # Captures matching notes by screened out update_ids, if the set of matches isn't empty
    if matching_set:
        matching_options = get_found_notes_by_update_ids(matching_set)
        create_inline_menu(matching_options, update)
        return MENU

    # Otherwise asks user to give it one more try
    else:
        update.message.reply_markdown(text=NOT_FOUND)
        update.message.reply_markdown(text=SEARCH_RESPONSE)
        return USER_SEARCH_QUERY


def help(update, context):
    # Displays the help message
    update.message.reply_markdown(text=HELP_MESSAGE, reply_markup=static_markup)

    return MENU


def cancel(update, context):
    # Interrupts the conversation
    update.message.reply_markdown(text=CANCEL, reply_markup=static_markup, quote=True)

    return MENU


def about(update, context):
    # Displays the /about/ info
    update.message.reply_animation('https://media.giphy.com/media/Fsn4WJcqwlbtS/giphy.gif')
    update.message.reply_markdown(text=ABOUT, reply_markup=static_markup)

    return MENU


def error(update, context):
    # Logs errors issued by updates
    logger.warning('Update %s caused error %s', update, context.error)


def main():
    # Starts the bot, creates the EventHandler and get the dispatcher to register handlers
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
                MENU: [MessageHandler(Filters.regex('^✍ New Note$'), take_note),
                       MessageHandler(Filters.regex('^👀 Search$'), search),
                       MessageHandler(Filters.regex('^🗒 List of Notes$'), notes_list),
                       ],

                USER_TYPES_NEW: [MessageHandler(Filters.text, write_new, pass_chat_data=True)],

                USER_SEARCH_QUERY: [MessageHandler(Filters.text, search_query, pass_chat_data=True)]
                },

        fallbacks=[CommandHandler('help', help),
                   CommandHandler('cancel', cancel),
                   CommandHandler('about', about)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
