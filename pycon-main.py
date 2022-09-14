from pyrogram import Client, emoji, filters
from pyrogram.types import (
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from random import sample, shuffle


app = Client("pycontzbot")


########## CAPTCHA AND WELCOME MESSAGE ##########

CAPTCHA_EMOJIS = [
    "SKULL",
    "ALARM_CLOCK",
    "WATERMELON",
    "SAFETY_PIN",
    "ROLL_OF_PAPER",
    "SPOON",
    "CUSTARD",
    "SPIDER",
    "SNAIL",
    "BEER_MUG",
    "COFFIN",
    "BIRTHDAY_CAKE",
    "LOCKED",
    "MICROSCOPE",
    "TROPHY",
    "BOMB",
    "LOBSTER",
    "PIZZA",
    "HAMBURGER",
    "GOAT",
    "ROSE",
    "BANANA",
    "BASEBALL",
    "CAMERA",
    "DOG",
    "MAGNET",
    "RAINBOW",
    "TOMATO",
    "SNOWMAN",
    "BONE",
]

MENTION = "[{}](tg://user?id={})"

MESSAGE = (
    "Welcome {}! Please select the emojis you see below. You are allowed 3 mistakes."
)


@app.on_message(filters.new_chat_members)
async def welcome(client, message):

    global captcha

    await message.delete()

    user_id = ",".join([str(u.id) for u in message.new_chat_members])
    user_id = int(user_id)

    await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions())

    new_members = [MENTION.format(i.first_name, i.id) for i in message.new_chat_members]

    message_text = MESSAGE.format(", ".join(new_members))

    list_of_emojis = [e for e in sample(CAPTCHA_EMOJIS, 9)]

    list_of_emojis = [emoji.__getattribute__(e) for e in list_of_emojis]

    captcha = [e for e in sample(list_of_emojis, 3)]

    captcha_text = " ".join(captcha)

    message_to_reply = await message.reply(
        f"{message_text}\n{captcha_text}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        list_of_emojis[0],
                        callback_data=f"{list_of_emojis[0]}.{user_id}",
                    ),
                    InlineKeyboardButton(
                        list_of_emojis[1],
                        callback_data=f"{list_of_emojis[1]}.{user_id}",
                    ),
                    InlineKeyboardButton(
                        list_of_emojis[2],
                        callback_data=f"{list_of_emojis[2]}.{user_id}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        list_of_emojis[3],
                        callback_data=f"{list_of_emojis[3]}.{user_id}",
                    ),
                    InlineKeyboardButton(
                        list_of_emojis[4],
                        callback_data=f"{list_of_emojis[4]}.{user_id}",
                    ),
                    InlineKeyboardButton(
                        list_of_emojis[5],
                        callback_data=f"{list_of_emojis[5]}.{user_id}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        list_of_emojis[6],
                        callback_data=f"{list_of_emojis[6]}.{user_id}",
                    ),
                    InlineKeyboardButton(
                        list_of_emojis[7],
                        callback_data=f"{list_of_emojis[7]}.{user_id}",
                    ),
                    InlineKeyboardButton(
                        list_of_emojis[8],
                        callback_data=f"{list_of_emojis[8]}.{user_id}",
                    ),
                ],
            ]
        ),
    )


app.run()
