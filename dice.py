import logging
import random
import re
import time
from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, InlineQueryHandler


def start(bot, update):
    update.message.reply_text("""Бот для игр в DnD
    Работает через встроенные запросы в любом чате
    Пример ввода
    @roller_dice_bot  2d6 + d5 - 4""")


def dice_summ(limit, amount):
    sample = []
    summ = 0
    for i in range(amount):
        sample.append(cryptogen.randint(1, limit))
    logging.log(logging.DEBUG, str(sample))
    for i in range(amount):
        summ += sample[i]
    return summ

def info_msg(results):
    results.append(InlineQueryResultArticle(id=uuid4(), title="Формат: 1d20 + d6 - 50 (числа до 100, не больше 10 пар)",
                                                input_message_content=InputTextMessageContent(
                                                        "Формат: 1d20 + d6 - 50 (числа до 100, не больше 10 пар)")))
    return results

def error_max_tokens(results):
    results.append(InlineQueryResultArticle(id=uuid4(), title="Числа до 100, не больше 10 пар",
                                                input_message_content=InputTextMessageContent(
                                                        "Числа до 100, не больше 10 пар")))
    return results

def dice_roll(bot, update):
    results = []
    #regexp for parse command
    reg_command = r'(^\d{0,2}d\d{1,2}$|^\d{1,2}$|^\d{0,2}d\d{1,2}([\+\-]\d{0,2}d\d{1,2}|[\+\-]\d{1,2})+$|^\d{1,2}([\+\-]\d{0,2}d\d{1,2}|[\+\-]\d{1,2})+$)'
    #regexp for matching tokens
    reg_tokens = r'(^\d{0,2}d\d{1,2}|^\d{1,2}|[\+\-]\d{0,2}d\d{1,2}|[\+\-]\d{1,2})'

    logging.log(logging.DEBUG, msg=("Request from ", update.inline_query.from_user.id, " at ", time.time()))

    query_string = update.inline_query.query
    query_solid = query_string.replace(' ', '')

    if re.search(reg_command, query_solid) is not None:
        tokens = re.findall(reg_tokens, query_solid)
        if len(tokens) > 10:
            error_max_tokens(results)
        elif len(tokens) == 0:
            info_msg(results)
        else:
            summ = 0

            for part in tokens:
                token = part if isinstance(part, str) else part[0]
                
                sign = 1
                if re.search(r'-', token) is not None:
                    sign = -1

                token = token.replace('-', '')
                token = token.replace('+', '')

                if re.search(r'd', token) is not None:
                    splits = re.split(r'd', token)
                    if splits[0] == '':
                        splits[0] = '1'

                    dices = dice_summ(int(splits[1]), int(splits[0]))
                    summ += sign * dices
                else:
                    summ += sign * int(token)
            
            results.append(InlineQueryResultArticle(id=uuid4(), title="Roll summ: {}".format(summ),
                                                    input_message_content=InputTextMessageContent("Request query: {}. Summ: {}".format(query_solid, summ))))
    else:
        info_msg(results)
    update.inline_query.answer(results, cache_time=0)
cryptogen = random.SystemRandom()


def initialize(token):
    logging.basicConfig(level=logging.DEBUG)

    updater = Updater(token=token)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(InlineQueryHandler(dice_roll))
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    updater.start_polling()
    updater.idle()
