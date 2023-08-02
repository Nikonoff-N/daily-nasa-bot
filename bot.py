import logging

from telegram import Update,User
from telegram.ext import Application, CommandHandler, ContextTypes,ConversationHandler,MessageHandler,filters,PicklePersistence

from api import *
from datetime import time

import os
import pytz

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
SUPERUSER = int(os.getenv('superuser'))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
    Start the bot and has important feature of adding user to sub list
    '''
    if update.effective_user in context.bot_data['sub_list']:
        await update.message.reply_text('Наш бот вас уже знает и будет отправлять сообщения.\n /help - все функции бота')
    else:
        context.bot_data['sub_list'].add(update.effective_user)
        await update.message.reply_text('Привет.Я каждый день буду присылать тебе красивые фото от NASA)')
        await update.message.reply_photo(context.bot_data['url'],context.bot_data['title']+"\n /more - подробнее")


async def send_data(context: ContextTypes.DEFAULT_TYPE):
    '''
    Each day this task will fectch data from nasa api and send it to all subs
    '''
    sub_list = context.bot_data['sub_list']
    data = await get_photo() #fetch data
    if data:# we got data
        context.bot_data['title'],context.bot_data['url'],context.bot_data['exp'] = data#save it for later
        context.bot_data['nasa_problems'] = False #mark that we have data today
        await context.bot.send_message(SUPERUSER,"Fetched data - success!") #send a messege to superviser
    else:
        context.bot_data['nasa_problems'] = True#no data today
        await context.bot.send_message(SUPERUSER,"Fetched data - fail!")

    #send nasa data
    for sub in sub_list:
        if context.bot_data['nasa_problems']:
            await sub.send_message("Неполадки в космической связи, сегодня без фото, простите((")
        else:
            await sub.send_photo(context.bot_data['url'],context.bot_data['title']+"\n /more - подробнее")


async def send_bot_data(context: ContextTypes.DEFAULT_TYPE):
    '''
    Send some general data to superviser, a task
    '''
    await context.bot.send_message(SUPERUSER,f"Количесвто пользователей:{len(context.bot_data['sub_list'])}\nNASA:{'Offline' if context.bot_data['nasa_problems'] else 'Online'}")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
    A simple list of command
    '''
    commands = [
        '/about - о создании бота',
        '/more - подробнее о фотографии',
        '/git - исходный код',
        '/feedback - оставить отзыв'

    ]
    await update.message.reply_text('\n'.join(commands))

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
    General info about bot
    '''
    await update.message.reply_text('Этот простенький бот демонстрирует возможности библиотеки python-telegram-bot с использованием JobQueue и picklepersistecy, задеплоен в docker-контейнере в Яндекс Облаке\nНиконов Дмитрий 2023 год')
    
async def git(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
    Provides link to bot source code
    '''
    await update.message.reply_text('https://github.com/Nikonoff-N/daily-nasa-bot')


async def feedback_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''
    Starts feedback conversation
    '''
    await update.message.reply_text('Что вы хотели бы передать разработчику?')
    return 1

async def feedback_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''
    Feedback conversation ender. Sends user feedback to superviser
    '''
    human = update.message.text
    await context.bot.send_message(SUPERUSER,f"Feedback:{human}\nfrom:@{update.effective_user.username}")
    await update.message.reply_text('Спасибо за отзыв!')
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''
    Mandatory fallback for conversation
    '''
    await update.message.reply_text('Отмена!')
    return ConversationHandler.END








async def more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Sends a photo explanation
    '''
    if context.bot_data['nasa_problems']:
        await update.message.reply_text("Неполадки в космической связи, сегодня без фото, простите((")
    else:
        await update.message.reply_text(context.bot_data['exp'])

async def init_data(application: Application):
    '''
    Inits first time user data. Does nothing if you already have some data stored by persistance/
    '''
    if 'sub_list' not in application.bot_data:
        application.bot_data['sub_list'] = set()
    if 'sub_list' not in application.bot_data:
        application.bot_data['nasa_problems'] = True

def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.\
    token = os.getenv('token')
    #File where bot data will be stored
    my_persistence = PicklePersistence(filepath='data.bin')
    #Start the bot and queue up init data 
    application = Application.builder().token(token).persistence(persistence=my_persistence).post_init(init_data).build()

    application.job_queue.run_daily(send_data,time=time(12,0,2,tzinfo=pytz.timezone('Europe/Moscow')),name="daily_user")#daily send data
    application.job_queue.run_daily(send_bot_data,time=time(13,0,2,tzinfo=pytz.timezone('Europe/Moscow')),name="daily_host")#daily send data

    feedback_handler = ConversationHandler(
        entry_points=[CommandHandler('feedback',feedback_start)],
        states = {
            1:[MessageHandler(filters.TEXT & ~filters.COMMAND,feedback_end)]
        },
        fallbacks=[CommandHandler('cancel',cancel)]
    )

    application.add_handler(feedback_handler)
    application.add_handler(CommandHandler('start',start))
    application.add_handler(CommandHandler("more", more))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("git", git))
    application.add_handler(CommandHandler("help", help))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()