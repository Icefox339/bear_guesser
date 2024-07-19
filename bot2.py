from operator import concat
from pickle import NONE
from socket import timeout
import telebot
from telebot import types
import os
import json
import numpy as np
import tensorflow as tf
import hashlib

from keras.api._v2.keras.preprocessing import image
from keras.api._v2.keras.preprocessing.image import ImageDataGenerator

from flask import Flask, request
 
 
USER_DATA_FILE = "user_data.json"
print("bot started")
TOKEN = ''
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()
flag = 0
spisok = {}
user_access = {}
REG_INIT = 1
LOGON = 2
ENTER = 3
app = Flask(__name__)
 
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    print()
    bot.process_new_updates([update])
    return '', 200

def load_model():
    return tf.keras.models.load_model("skibidi_model.h5")
 
def save_user_data(user_data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(user_data, file)
 
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    else:
        return {}

@bot.message_handler(commands=['stop'])
def stop(message):
    global flag
    flag = 0
    bot.send_message(message.chat.id, "Stopped. Whachagonado??")
 
 
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/login")
    btn2 = types.KeyboardButton("/register") 
    btn3 = types.KeyboardButton("/predict")
    btn4 = types.KeyboardButton("/logout")
 
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)
    bot.send_message(message.chat.id,"Henlo, {0.first_name}!\nMy stuff:\n/register - create an account;\n/login - enter;\n/predict - guess image;\n/logout - exit bot".format(message.from_user,bot.get_me()),reply_markup=markup, parse_mode='html')
 
@bot.message_handler(commands=['register'])
def register(message):
    global flag
    global user_data
    user_data = load_user_data()
    id = str(message.from_user.id)
    if id in user_data:
        bot.send_message(message.chat.id, "You had already been signed up before")
    else:
        bot.send_message(message.chat.id, "Create a password for your account")
        flag = LOGON
 
@bot.message_handler(commands=['login'])
def login(message):
    global flag
    global user_data
    global user_access
    user_data = load_user_data()
    id = message.from_user.id
    if id in user_access and user_access[id]:
        bot.send_message(message.chat.id, "You are signed in")
    else:
        bot.send_message(message.chat.id, "Enter your password:")
        flag = ENTER
 
 
@bot.message_handler(commands=['logout'])
def logout(message):
    global flag
    global user_access
    id = message.from_user.id
    if (id in user_access):
        if user_access[id]:
            user_access[id] = 0
            bot.send_message(message.chat.id,"Successful logout")
        else:
            bot.send_message(message.chat.id,"You should sign in")
    else:
        bot.send_message(message.chat.id,"You should sign up")
 
@bot.message_handler(commands=['predict'])
def predict(message):
    global flag
    global user_access
    id = message.from_user.id
    if user_access.get(id, 0):
        flag = ENTER
        bot.send_message(message.chat.id, "Send me an image")
    else:
        bot.send_message(message.chat.id, "Use login to have an access")
 
@bot.message_handler(content_types=['text'])
def get_pass(message):
    global flag
    global user_data
    global user_access
    global current_login
    match flag:
        case 1:
            id = message.from_user.id
            login = id
            bot.send_message(message.chat.id, "Enter your password:")
            user_data[login] = {"id": id, "password": None}
            current_login = id  
            flag = LOGON
        case 2:
            id = message.from_user.id
            login = str(id)
            user_data[login] = {"id": id, "password": None}
            password = message.text
            password = hashlib.sha256(password.encode()).hexdigest()
            user_data[login]["password"] = password  
            bot.send_message(message.chat.id, "Sign up successful")
            flag = 0
            save_user_data(user_data)  
        case 3:
            password = message.text
            id = message.from_user.id
            current_login = str(id)
            print(user_data.get(current_login, {}).get("password"))
            print(hashlib.sha256(password.encode()).hexdigest())
            if user_data.get(current_login, {}).get("password") == hashlib.sha256(password.encode()).hexdigest(): 
                user_access[id] = 1
                bot.send_message(message.chat.id, "Auth has been completed")
            else:
                bot.send_message(message.chat.id, "Invalid password")
            flag = 0
            save_user_data(user_data)
 
@bot.message_handler(content_types=['photo'])
def get_photo(message):
    global flag
    if flag == ENTER:
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = file_info.file_path
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id,"Processing")
        print("plaki plaki")
        model = load_model()
        print("ili normaldaki?")
        img = image.load_img(src, target_size=(200, 200))
        print("1")
        x = image.img_to_array(img)
        print("2")
        x = np.expand_dims(x, axis=0)
        print("3")
        images = np.vstack([x])
        print("4")
        classes = model.predict(images, batch_size=10)
        print("normaldaki")
        if classes[0] < 0.5:
            bot.send_message(message.chat.id,"This is Humamn")
        else:
            bot.send_message(message.chat.id,"This is Beeeearrr")
 
        bot.send_message(message.chat.id, "Semme a picture rq or leave /stop")
    else:
        bot.send_message(message.chat.id, "SIGN IN BEFORE USING PREDICT")
 
def start_flask():
    webhook_url = '.ngrok-free.app/webhook'
 
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
 
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
 
if __name__ == '__main__':
    start_flask()