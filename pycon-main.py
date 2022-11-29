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
async def captcha_function(client: Client, query):

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
                f"Welcome to Pycon Tanzania [{query.from_user.first_name}](tg://user?id={target}).\n\nPlease Follow the Rules of the Groupchat. Click **`Help`** below for more information.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Help",
                                callback_data=f"helpmenu",
                            ),
                        ]
                    ]
                ),
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


########## HELP COMMAND ##########


@app.on_message(
    filters.command(commands="help", prefixes=["/", "#", "!"], case_sensitive=False)
)
@app.on_callback_query(filters.regex(r"helpmenu"))
async def help_menu_function(client, message):

    to_respond = "reply" if type(message) == Message else "edit_message_text"

    if to_respond == "edit_message_text":
        await message.answer()
    if to_respond == "reply":
        await message.delete()

    await getattr(message, to_respond)(
        text="Welcome To Pycon Tanzania",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Rules",
                        callback_data="rules.helpresponse",
                    ),
                    InlineKeyboardButton(
                        "About",
                        callback_data="about.helpresponse",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Events",
                        callback_data="events.helpresponse",
                    ),
                    InlineKeyboardButton(
                        "Announcements",
                        callback_data="announcementsmenu",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Resources",
                        callback_data="resources.helpresponse",
                    ),
                    InlineKeyboardButton(
                        "Administrator",
                        callback_data="adminmenu",
                    ),
                ],
            ]
        ),
    )


RESOURCES = """
**Here are some good resources to learn Python:**

• [Official Tutorial](https://docs.python.org/3/tutorial/index.html) - Book
• [Dive Into Python 3](https://www.diveinto.org/python3/table-of-contents.html) - Book
• [Hitchhiker's Guide!](https://docs.python-guide.org) - Book
• [Learn Python](https://www.learnpython.org/) - Interactive
• [Project Python](http://projectpython.net) - Interactive
• [Python Video Tutorials](https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU) - Video
• [MIT OpenCourseWare](http://ocw.mit.edu/6-0001F16) - Course
• @PythonRes - Channel
"""

RULES = """
**Rules of the Group:**

 • All conversations must be in English or Kiswahili

 • Business advertisements without proper authorization will lead to a ban

 • Any Forex, Crypto, Trading and related content will lead to a ban

 • Disrespect will not be tolerated in the group chat

"""

HELP_SWITCHER = {
    "rules": RULES,
    "about": "A Community of Professionals, Entrepreneurs, Scientists & Students Collaborating to Innovate & Advance Python Language Usage. Contact secretariat@pycon.or.tz or visit our website: https://pycon.or.tz",
    "events": "Our next Pycon Meeting will be in Zanzibar on Dec 2022. Stay tuned for updates",
    "announcements": "There are no announcements at the moment",
    "resources": RESOURCES,
}


@app.on_callback_query(filters.regex(r"helpresponse"))
async def help_menu_response(client: Client, query: CallbackQuery):

    queried = query.data.split(".")[0]
    await query.answer()
    await query.edit_message_text(
        text=HELP_SWITCHER[queried],
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Back To Menu",
                        callback_data=f"helpmenu",
                    ),
                ]
            ]
        ),
    )


@app.on_callback_query(filters.regex(r"adminmenu"))
async def admin_help_function(client: Client, query: CallbackQuery):

    queried = query.data.split(".")[0]
    await query.answer()
    await query.edit_message_text(
        text="Here are the Administrative Commands:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Mute",
                        callback_data="mute.adminresponse",
                    ),
                    InlineKeyboardButton(
                        "Ban",
                        callback_data="ban.adminresponse",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Delete",
                        callback_data="delete.adminresponse",
                    ),
                    InlineKeyboardButton(
                        "Promote",
                        callback_data="promote.adminresponse",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Back To Menu",
                        callback_data=f"helpmenu",
                    ),
                ],
            ]
        ),
    )


ADMIN_HELP_SWITCHER = {
    "mute": "Respond to a chat with **`/mute`** to mute the sender",
    "ban": "Respond to a chat with **`/ban`** to ban the sender",
    "delete": "Respond to a chat with **`/delete`** to delete the message",
    "promote": "Respond to a chat with **`/promote`** to give the sender admin privileges",
}


@app.on_callback_query(filters.regex(r"adminresponse"))
async def admin_response_function(client: Client, query: CallbackQuery):

    queried = query.data.split(".")[0]
    await query.answer()
    await query.edit_message_text(
        text=ADMIN_HELP_SWITCHER[queried],
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Back",
                        callback_data="adminmenu",
                    ),
                    InlineKeyboardButton(
                        "Help Menu",
                        callback_data="helpmenu",
                    ),
                ]
            ]
        ),
    )


############ ANNOUNCEMENTS ##################


@app.on_callback_query(filters.regex(r"announcementsmenu"))
async def announcements_menu_function(client: Client, query: CallbackQuery):

    await query.answer()
    await query.edit_message_text(
        text="PyCon Tanzania Starts on 5th December",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Topics",
                        callback_data="topics",
                    ),
                    InlineKeyboardButton(
                        "Speakers",
                        callback_data="speakers",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Events",
                        callback_data="events",
                    ),
                    InlineKeyboardButton(
                        "Back To Menu",
                        callback_data=f"helpmenu",
                    ),
                ],
            ]
        ),
    )


AllTopics = """
*AI Transformers and Self-Attention*
```by Isack Odero```

*Analysing the Development of Cervical Cancer Using ML*
```by Eng. Saida Nyasasi```

*Explainability for Natural Language Processing*
```by Antony Mipawa```

*Fun Simple Python Programs*
```by Monalisa Mbilinyi```

*Geospatial Data Analysis Using Python*
```by Khairiya Masoud```

*NLP for African Languages and Building Chatbots with Sarufi*
```by Antony Mipawa and Kalebu Gwalugano```

*Network Analysis Made Simple Using NetworkX*
```by Mridul Seth```

*Poultry Disease Diagnosis with Deep Learning*
```by Dr. Dina Machuve```

*Predicting Fake News Using GCN*
```by Zephania Reuben```

*Programming Embedded IoT with Python*
```by Mahir Nasor```

*Python Language Foundation*
```by Abubakar Omar and Joan Henry```

*Python Web Development with Django*
```by Lugano Ngulwa```

*Species Determination of Malaria Vectors Using AI*
```by Issa Mshani```

*WebScrapping of Consumer Prices*
```by Alban Manishimwe```

*WebScrapping with Beautiful Soup*
```by Nathaniel Mwaipopo```

*Why is Data Science Necessary, Why Now?*
```by Hassan Kibirige```
"""


@app.on_callback_query(filters.regex(r"topics"))
async def topics(client: Client, query: CallbackQuery):

    await query.answer()
    await query.edit_message_text(
        text=f"The following will be discussed:\n\n{AllTopics}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Back",
                        callback_data="announcementsmenu",
                    ),
                    InlineKeyboardButton(
                        "Back To Menu",
                        callback_data=f"helpmenu",
                    ),
                ],
            ]
        ),
    )


AllSpeakers = """
*Abubakar Omar*
```Python Teacher```

*Alban Manishimwe*
```Uganda Bureau of Statistics```

*Antony Mipawa*
```Software Developer Neurotech```

*Dr. Dina Machuve*
```Co-Founder DevData Analytics```

*Eng. Saida Nyasasi*
```ED & Researcher iSuite```

*Hassan Kibirige*
```Author of Plotnine Python Library```

*Isack Odero*
```Founder NileAGI```

*Issa Mshani*
```Research Scientist Ifakara Health Institute```

*Joan Henry*
```Software Developer```

*Kalebu Gwalugano*
```Founder Neurotech```

*Khairiya Masoud*
```State University of Zanzibar```

*Lugano Ngulwa*
```Software Developer```

*Mahir Nasor*
```Z TechHub Zanzibar```

*Monalisa Mbilinyi*
```Python Software Developer```

*Mridul Seth*
```Python Software Developer```

*Nathaniel Mwaipopo*
```Python Software Developer```

*Zephania Reuben*
"""


@app.on_callback_query(filters.regex(r"speakers"))
async def speakers(client: Client, query: CallbackQuery):

    await query.answer()
    await query.edit_message_text(
        text=f"The following will be the our event speakers:\n\n{AllSpeakers}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Back",
                        callback_data="announcementsmenu",
                    ),
                    InlineKeyboardButton(
                        "Back To Menu",
                        callback_data=f"helpmenu",
                    ),
                ],
            ]
        ),
    )


AllEvents = """
5th | December | 2022

09:00-09:30: Opening Keynotes

09:30-10:30: Loren Crary

10:30-10:45: Break

10:45-11:15: Foundations of Python Bootcamp

11:15-11:45: Foundations of Python Bootcamp

11:45-13:15: Lunch

13:15-13:45: Django Web Development

13:45-14:15: Django Web Development

14:15-14:30: Break

14:30-15:00: Network Analysis Made Simple Using NetworkX

15:00-15:30: Network Analysis Made Simple Using NetworkX

15:30-15:45: Break

15:45-16:15: Hackathon - NLP for African Languages Building Chatbots with Sarufi

16:15-16:45: Hackathon - NLP for African Languages Building Chatbots with Sarufi

16:45-17:00: PyCon Social Event

6th | December | 2022

09:00-09:30: Hackathon - NLP for African Languages Building Chatbots with Sarufi

09:30-10:30: Tigo Hackathon

10:30-10:45: Break

10:45-11:15: Hackathon - NLP for African Languages Building Chatbots with Sarufi

11:15-11:45: Tigo Hackathon

11:45-13:15: Lunch

13:15-13:45: Hackathon - NLP for African Languages Building Chatbots with Sarufi

13:45-14:15: Tigo Hackathon

14:15-14:30: Break

14:30-15:00: Hackathon - NLP for African Languages Building Chatbots with Sarufi

15:00-15:30: Tigo Hackathon

15:30-15:45: Break

15:45-16:15: Hackathon - NLP for African Languages Building Chatbots with Sarufi

16:15-16:45: Hackathon Birds of Feather (BOF)

16:45-17:00: PyCon Social Event

7th | December | 2022

09:00-09:30: Why is Data Science Necessary, Why Now?

09:30-10:30: Geospatial Data Analysis Using Python

10:30-10:45: Break

10:45-11:15: Species Determination of Malaria Vectors Using AI

11:15-11:45: Python Development Tigo

11:45-13:15: Lunch

13:15-13:45: Analysing the Development of Cervical Cancer Using ML

13:45-14:15: Explainability for Natural Language Processing

14:15-14:30: Break

14:30-15:00: Predicting Fake News Using GCN

15:00-15:30: Poultry Disease Diagnosis with Deep Learning

15:30-15:45: Break

15:45-16:15: AI Transformers and Self-Attention

16:15-16:45:  Panel Discussion on DS/ML/AI

16:45-17:00: PyCon Social Event

8th | December | 2022

09:00-09:30: Fun Simple Python Programs

09:30-10:30: Python Development Tigo

10:30-10:45: Break

10:45-11:15: Programming Embedded IoT with Python

11:15-11:45: Python Web Development with Django

11:45-13:15: Lunch

13:15-13:45: WebScrapping of Consumer Prices

13:45-14:15: Testing Smart Contracts with Pytest & Brownie

14:15-14:30: Break

14:30-15:00: WebScrapping with Beautiful Soup

15:00-15:30: Lightening Talks Pyladies

15:30-15:45: Break

15:45-16:15: Lightening Talks Pyladies

16:15-16:45: Business Analysis with AI. Inspiring Women in AI. Teaching Python To Learn Python.

16:45-17:00: Closing Keynote, DG ICT Commission

"""


@app.on_callback_query(filters.regex(r"events"))
async def events(client: Client, query: CallbackQuery):

    await query.answer()
    await query.edit_message_text(
        text=f"Here's the events timetable:\n\n{AllEvents}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Back",
                        callback_data="announcementsmenu",
                    ),
                    InlineKeyboardButton(
                        "Back To Menu",
                        callback_data=f"helpmenu",
                    ),
                ],
            ]
        ),
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
        await message.delete()
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
    message_to_reply = await message.reply(
        f"Promoted [{message.reply_to_message.from_user.first_name}](tg://user?id={to_be_promoted})"
    )
    await asyncio.sleep(30)
    await message_to_reply.delete()
    await message.delete()


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
