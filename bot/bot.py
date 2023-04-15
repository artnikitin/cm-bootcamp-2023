import os
import logging
import numpy as np
import random
from time import sleep
from coolname import generate
from mlem.api import load
from mlem.runtime.client import HTTPClient
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# create a telegram bot and paste it here, or use `flyctl secrets set TELEGRAM_TOKEN=token` to set it secretly
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TOKEN")
# add URL of you REST API app here
client = HTTPClient(host="https://art-expert-collmach.fly.dev", port=None)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

PAINTER, FIRST_BID, SECOND_BID, THIRD_BID, LAST_BID, REFUSE = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [["/auction", "/eval"]]

    await update.message.reply_text(
        f"Привет, {update.effective_user.first_name}! Меня зовут Сотби, и я <a href='https://translate.academic.ru/лицитатор/en/ru/'>лицитатор</a> (не смейся). \n\n"
        f"Давай поиграем в аукцион. Набери /auction, чтобы продолжить или /eval для перехода к оценке изображений.",
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )


async def auction_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает аукцион и спрашивает имя художника картины."""
    reply_keyboard = [["Ван Гог", "Левитан", "Айвазовский"]]
    
    await update.message.reply_text("Аукцион начинается! Сегодняшний лот №123:")
    await update.message.reply_photo(photo="van_gog_first.jpg")
    await update.message.reply_text(
        f"Узнаешь, чья это картина? В смысле, кто ее нарисовал, конечно, а не купил.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )
    
    return PAINTER


async def painter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет имя художника картины и спрашивает первую ставку."""
    painter = update.message.text
    if painter == "Ван Гог":
        await update.message.reply_text(
            f"Верно! Ты знаешь толк в искусстве! Это картина голландского художника Винсента Ван Гога "
            f"«Ваза с ромашками и маками»",
            reply_markup=ReplyKeyboardRemove(),
        )
        sleep(2)
    else:
        await update.message.reply_text(
            f"Современные богачи такие невежды! Это картина голландского художника Винсента Ван Гога "
            f"«Ваза с ромашками и маками»",
            reply_markup=ReplyKeyboardRemove(),
        )
        sleep(2)
    await update.message.reply_text(
            f"Начинаем аукцион! Стартовая цена $25. Можно ставить любую сумму, главное, чтобы это было целое число. Итак, твоя ставка?"
    )
    return FIRST_BID

async def first_bid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет имя художника картины и спрашивает первую ставку."""
    start_bid = 25
    first_bid_amount = update.message.text
    user = update.message.from_user.first_name
    try:
        first_bid_amount = int(first_bid_amount)
    except ValueError:
        await update.message.reply_text(
        "Ставка должна быть целым числом. Попробуй еще раз."
    )
        return FIRST_BID
    
    if first_bid_amount <= start_bid:
        await update.message.reply_text(
        "Ставка должна быть больше. Изначальной или предыдушей ставки. Попробуй еще раз."
    )
        return FIRST_BID
    
    first_answer_bid = random.randint(round(first_bid_amount + first_bid_amount * 0.5), round(first_bid_amount + first_bid_amount * 0.9))
    await update.message.reply_text(
        "{} сделал ставку ${}. Кто-нибудь еще? Дама в красном - ${}".format(user, first_bid_amount, first_answer_bid)
    )
    context.user_data["start_bid"] = first_answer_bid
    
    return SECOND_BID

async def second_bid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет имя художника картины и спрашивает первую ставку."""
    start_bid = context.user_data["start_bid"]
    second_bid_amount = update.message.text
    user = update.message.from_user.first_name
    try:
        second_bid_amount = int(second_bid_amount)
    except ValueError:
        await update.message.reply_text(
        "Ставка должна быть целым числом. Попробуй еще раз."
    )
        return SECOND_BID
    
    if second_bid_amount <= start_bid:
        await update.message.reply_text(
        "Ставка должна быть больше. Изначальной или предыдушей ставки. Попробуй еще раз."
    )
        return SECOND_BID
    
    second_answer_bid = random.randint(round(second_bid_amount + second_bid_amount * 0.5), round(second_bid_amount + second_bid_amount * 0.9))
    await update.message.reply_text(
        "{} сделал ставку ${}. Кто-нибудь еще? Мужчина в заднем ряду - ${}".format(user, second_bid_amount, second_answer_bid)
    )
    context.user_data["start_bid"] = second_answer_bid
    
    return THIRD_BID

async def third_bid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет имя художника картины и спрашивает первую ставку."""
    start_bid = context.user_data["start_bid"]
    third_bid_amount = update.message.text
    user = update.message.from_user.first_name
    try:
        third_bid_amount = int(third_bid_amount)
    except ValueError:
        await update.message.reply_text(
        "Ставка должна быть целым числом. Попробуй еще раз."
    )
        return THIRD_BID
    
    if third_bid_amount <= start_bid:
        await update.message.reply_text(
        "Ставка должна быть больше. Изначальной или предыдушей ставки. Попробуй еще раз."
    )
        return THIRD_BID
    
    third_answer_bid = random.randint(round(third_bid_amount + third_bid_amount * 0.5), round(third_bid_amount + third_bid_amount * 0.9))
    third_answer_bid += 1_000_000
    await update.message.reply_text(
        "{} сделал ставку ${}. Кто-нибудь еще? Илон Маск - ${}".format(user, third_bid_amount, third_answer_bid)
    )
    await update.message.reply_text(
        "Повысь ставку или откажись два раза нажав на /refuse"
    )
    context.user_data["start_bid"] = third_answer_bid
    
    return LAST_BID

async def last_bid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет имя художника картины и спрашивает первую ставку."""
    start_bid = context.user_data["start_bid"]
    last_bid_amount = update.message.text
    user = update.message.from_user.first_name
    if last_bid_amount == "/refuse":
        return REFUSE
    else:
        try:
            last_bid_amount = int(last_bid_amount)
        except ValueError:
            await update.message.reply_text(
            "Ставка должна быть целым числом. Попробуй еще раз."
        )
            return LAST_BID
        
        if last_bid_amount <= start_bid:
            await update.message.reply_text(
            "Ставка должна быть больше. Изначальной или предыдушей ставки. Попробуй еще раз."
        )
            return LAST_BID
    sleep(1)
    await update.message.reply_text("Илон Маск в шоке!")
    sleep(1)
    await update.message.reply_text("${} раз!".format(last_bid_amount))
    sleep(2)
    await update.message.reply_text("${} два!".format(last_bid_amount))
    sleep(2)
    await update.message.reply_text("${} три!".format(last_bid_amount))
    sleep(2)
    await update.message.reply_text("Картина Ван Гога «Ваза с ромашками и маками» отходит {}! Поздравляю!".format(user))
    sleep(1)
    await update.message.reply_photo(photo="van_gog_take.jpg")
    
    close_bid = 61_800_000 - 61_800_000 * 0.3 < last_bid_amount < 61_800_000 + 61_800_000 * 0.3
    
    if close_bid:
        sleep(2)
        await update.message.reply_text(
            f"Это, конечно, все шутка. Данная картина была продана на аукционе Sotheby's в Нью-Йорке в 2014 году "
            f"за $61,8 млн. Но ты почти угадал!"
        )
    else:
        sleep(2)
        await update.message.reply_text(
            f"Это, конечно, все шутка. Данная картина была продана на аукционе Sotheby's в Нью-Йорке в 2014 году "
            f"за $61,8 млн. Так что, наш маленький аукцион немного смешной!"
        )
    sleep(2)
    await update.message.reply_text(
            
            "Картина была написана в 1890 году всего за несколько недель до смерти художника во Франции в доме врача Ван Гога Пола Хакетта и была одной из немногих, проданных голландским художником при жизни.\n\n"
            "В 1928 году ее купил Конгер Гудиер, один из основателей Музея современного искусства, а ее последний владелец купил картину в 1990 году.\n\n"
            "В 2014 году «Вазу с ромашками и маками» продали на $10 млн дороже, чем оценивали независимые оценщики.\n\n"
        )
    sleep(2)
    await update.message.reply_text(
        "Набери /eval, если хочешь увидеть больше цен с аукциона Sotheby's."
        )
    
    
    return ConversationHandler.END

async def refuse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отказывает делать ставку и завершает аукцион."""
    last_answer_bid = context.user_data["start_bid"]
    await update.message.reply_text("${} раз!".format(last_answer_bid))
    sleep(2)
    await update.message.reply_text("${} два!".format(last_answer_bid))
    sleep(2)
    await update.message.reply_text("${} три!".format(last_answer_bid))
    sleep(1)
    await update.message.reply_text("Картина Ван Гога «Ваза с ромашками и маками» отходит господину Илону Маску!")
    sleep(2)
    await update.message.reply_text(
            f"Это, конечно, все шутка. Данная картина была продана на аукционе Sotheby's в Нью-Йорке в 2014 году "
            f"за $61,8 млн. Так что, наш маленький аукцион немного смешной!"
        )
    sleep(2)
    await update.message.reply_text(
            
            "Картина была написана в 1890 году всего за несколько недель до смерти художника во Франции в доме врача Ван Гога Пола Хакетта и была одной из немногих, проданных голландским художником при жизни.\n\n"
            "В 1928 году ее купил Конгер Гудиер, один из основателей Музея современного искусства, а ее последний владелец купил картину в 1990 году.\n\n"
            "В 2014 году «Вазу с ромашками и маками» продали на $10 млн дороже, чем оценивали независимые оценщики.\n\n"
        )
    sleep(2)
    await update.message.reply_text(
        "Набери /eval, если хочешь увидеть больше цен с аукциона Sotheby's."
        )
    
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Аукцион завершен!", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
    
    
async def evaluation_suggest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        """
        Если хочешь узнать, сколько бы стоила твоя картина на реальном аукционе Sotheby's, присылай фото, а я оценю!"
        """,
        reply_markup=ReplyKeyboardRemove()
        )
  
    
async def estimate_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive('user_photo.jpg')

    res = client.predict("user_photo.jpg")

    pic_name = " ".join(generate(np.random.randint(2, 5))).capitalize()
    caption = f"""За такую картину на аукционе Sotheby's пришлось бы заплатить ориентировочно: ${{price}}"""
    # Price is estimated using Sothebys.com data
    # Other characteristics can be predicted using Wikiart data

    await update.message.reply_photo(
        update.message.photo[-1].file_id,
        caption=caption.format(
            price=round(res["price"]),
            author=update.effective_user.full_name,
        )
    )

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("auction", auction_start)],
        states={
            PAINTER: [MessageHandler(filters.Regex("^(Ван Гог|Левитан|Айвазовский)$"), painter)],
            FIRST_BID: [MessageHandler(filters.TEXT, first_bid)],
            SECOND_BID: [MessageHandler(filters.TEXT, second_bid)],
            THIRD_BID: [MessageHandler(filters.TEXT, third_bid)],
            LAST_BID: [MessageHandler(filters.TEXT, last_bid)],
            REFUSE: [CommandHandler("refuse", refuse)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    
    
    app.add_handler(MessageHandler(filters.TEXT, evaluation_suggest))
    app.add_handler(CommandHandler("eval", evaluation_suggest))
    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(MessageHandler(filters.PHOTO, estimate_price))
    

    app.run_polling()


if __name__ == "__main__":
    main()
