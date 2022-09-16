from pyrogram import Client, emoji, filters, enums
from pyrogram.types import (
    CallbackQuery,
    Chat,
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)
import asyncio
from datetime import datetime, timedelta
from random import sample, shuffle

app = Client("pycontzbot")

########## CUSTOM FILTER TO IDENTIFY ADMINS ##########


async def check_admin_filter(_, client: Client, message: Message):
    user = await client.get_chat_member(
        chat_id=message.chat.id, user_id=message.from_user.id
    )
    return bool(
        user.status == enums.ChatMemberStatus.OWNER
        or user.status == enums.ChatMemberStatus.ADMINISTRATOR
    )


check_admin = filters.create(check_admin_filter)

########## CAPTCHA AND WELCOME MESSAGE ##########

CAPTCHA_EMOJIS = [
    "SKULL",
    "ALARM_CLOCK",
    "WATERMELON",
    "SAFETY_PIN",
    "ROLL_OF_PAPER",
    "SPOON",
    "CUSTARD",
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

    captcha_text = "      ".join(captcha)

    message_to_reply = await message.reply(
        f"{message_text}\n\n\n{captcha_text}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        list_of_emojis[0],
                        callback_data=f"{list_of_emojis[0]}.captcha",
                    ),
                    InlineKeyboardButton(
                        list_of_emojis[1],
                        callback_data=f"{list_of_emojis[1]}.captcha",
                    ),
                    InlineKeyboardButton(
                        list_of_emojis[2],
                        callback_data=f"{list_of_emojis[2]}.captcha",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        list_of_emojis[3],
                        callback_data=f"{list_of_emojis[3]}.captcha",
                    ),
                    InlineKeyboardButton(
                        list_of_emojis[4],
                        callback_data=f"{list_of_emojis[4]}.captcha",
                    ),
                    InlineKeyboardButton(
                        list_of_emojis[5],
                        callback_data=f"{list_of_emojis[5]}.captcha",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        list_of_emojis[6],
                        callback_data=f"{list_of_emojis[6]}.captcha",
                    ),
                    InlineKeyboardButton(
                        list_of_emojis[7],
                        callback_data=f"{list_of_emojis[7]}.captcha",
                    ),
                    InlineKeyboardButton(
                        list_of_emojis[8],
                        callback_data=f"{list_of_emojis[8]}.captcha",
                    ),
                ],
            ]
        ),
    )


captcha_checker = set()  # will confirm our captcha
number_of_tries = 0  # kick user if it reaches 3


@app.on_callback_query(filters.regex(r"captcha"))
async def captcha_function(client, query):

    global captcha_checker, number_of_tries

    replier = query.from_user.id  # one who answered the captcha
    target = query.message.entities[0].user.id  # target of the captcha

    emoji_response = query.data.split(".")[0]

    if replier != target:
        await query.answer("This message is not for you!", show_alert=True)
        return
    if emoji_response in captcha:
        captcha_checker.add(emoji_response)
        await query.answer(text="Correct!", cache_time=1)
        if len(captcha_checker) == len(captcha):
            new_welcome_message = await query.edit_message_text(
                f"Welcome to Pycon Tanzania [{query.from_user.first_name}](tg://user?id={target})"
            )
            await client.restrict_chat_member(
                query.message.chat.id,
                target,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                ),
            )
            captcha_checker = set()
            number_of_tries = 0
            await asyncio.sleep(30)
            await new_welcome_message.delete()

    elif number_of_tries == 2:
        await query.answer("You have been banned for 60 seconds", show_alert=True)
        await asyncio.sleep(5)
        kicker = await client.ban_chat_member(
            query.message.chat.id,
            target,
            datetime.now() + timedelta(seconds=60),  # Kick user from chat for a minute
        )
        await kicker.delete()
        await query.message.delete()

        captcha_checker = set()
        number_of_tries = 0

    elif emoji_response not in captcha:
        await query.answer(text="Wrong!", cache_time=1)
        number_of_tries += 1


@app.on_message(filters.left_chat_member)
async def member_left_group(client, message):
    await message.delete()


########## RULES AND CoC ##########


@app.on_message(
    filters.command(commands="rules", prefixes=["/", "#", "!"], case_sensitive=False)
)
async def rules(client, message: Message):
    await message.reply(text="These are the Rules of the Group:")  # Will be added


########## HELP COMMAND ##########


@app.on_message(
    filters.command(commands="help", prefixes=["/", "#", "!"], case_sensitive=False)
)
async def rules(client, message: Message):
    await message.reply(
        text="""Here is a list of available commands:

`/rules`: To get Rules of the groupchat

**ADMIN COMMANDS:**

`/mute`: To mute an individual

`/ban`: To ban an individual

`/delete`: To delete a message

`/promote`: To promote someone to adminship
"""
    )


########## MUTE COMMAND ##########


@app.on_message(
    filters.command(commands="mute", prefixes=["!", "/", "#"]) & check_admin
)
async def mute(client: Client, message: Message):

    if not message.reply_to_message:
        return

    user = await client.get_chat_member(
        chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id
    )

    if (
        user.status == enums.ChatMemberStatus.OWNER
        or user.status == enums.ChatMemberStatus.ADMINISTRATOR
    ):
        message_to_reply = await message.reply(text="Cannot Mute Admins")
        await asyncio.sleep(5)
        await message_to_reply.delete()
        await message.reply_to_message.delete()
        return

    await message.reply_to_message.delete()
    await client.restrict_chat_member(
        message.chat.id,
        message.reply_to_message.from_user.id,
        ChatPermissions(),
        datetime.now() + timedelta(hours=6),
    )
    await message.reply(
        text=f"[{message.reply_to_message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id}) has been muted for 6 hours.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Unmute", f"unmute.{message.reply_to_message.from_user.id}"
                    )
                ]
            ]
        ),
    )


@app.on_callback_query(filters.regex(r"unmute"))
async def unmute(client: Client, query: CallbackQuery):

    to_be_unmuted = query.data.split(".")[1]
    text = query.message.text

    user = await client.get_chat_member(
        chat_id=query.message.chat.id, user_id=query.from_user.id
    )

    if not (
        user.status == enums.ChatMemberStatus.OWNER
        or user.status == enums.ChatMemberStatus.ADMINISTRATOR
    ):
        await query.answer("Only admins can perform this action", show_alert=True)
        return

    await client.restrict_chat_member(
        query.message.chat.id,
        to_be_unmuted,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True,
        ),
    )

    await query.edit_message_text(f"~~{text.markdown}~~\n\nYou have been Unmuted")


######## BAN COMMAND ########


@app.on_message(filters.command(commands="ban", prefixes=["!", "/", "#"]) & check_admin)
async def ban(client: Client, message: Message):

    if not message.reply_to_message:
        return

    user = await client.get_chat_member(
        chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id
    )

    if (
        user.status == enums.ChatMemberStatus.OWNER
        or user.status == enums.ChatMemberStatus.ADMINISTRATOR
    ):
        message_to_reply = await message.reply(text="Cannot Ban Admins")
        await asyncio.sleep(5)
        await message_to_reply.delete()
        await message.delete()
        return

    await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    await message.reply_to_message.delete()
    await message.reply(
        text=f"[{message.reply_to_message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id}) has been permanently banned.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Unban", f"unban.{message.reply_to_message.from_user.id}"
                    )
                ]
            ]
        ),
    )


@app.on_callback_query(filters.regex(r"unban"))
async def unban(client: Client, query: CallbackQuery):

    to_be_unbanned = query.data.split(".")[1]
    text = query.message.text

    user = await client.get_chat_member(
        chat_id=query.message.chat.id, user_id=query.from_user.id
    )

    if not (
        user.status == enums.ChatMemberStatus.OWNER
        or user.status == enums.ChatMemberStatus.ADMINISTRATOR
    ):
        await query.answer("Only admins can perform this action", show_alert=True)
        return

    await client.unban_chat_member(query.message.chat.id, to_be_unbanned)

    await query.edit_message_text(f"~~{text.markdown}~~\n\nYou have been Unbanned")


########## PROMOTE ADMIN ##########
@app.on_message(
    filters.command(commands="promote", prefixes=["!", "/", "#"]) & check_admin
)
async def promote(client: Client, message: Message):

    to_be_promoted = message.reply_to_message.from_user.id
    chat_id = message.chat.id

    await client.promote_chat_member(chat_id, to_be_promoted)
    await message.reply(
        f"Promoted [{message.reply_to_message.from_user.first_name}](tg://user?id={to_be_promoted})"
    )


########## DELETE MESSAGES ##########
@app.on_message(
    filters.command(commands="delete", prefixes=["!", "/", "#"]) & check_admin
)
async def delete_a_message(client: Client, message: Message):

    if not message.reply_to_message:
        await message.delete()
        return
    await message.delete()
    await message.reply_to_message.delete()


app.run()
