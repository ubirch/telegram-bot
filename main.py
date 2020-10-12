import base64
import hashlib
import time 
import urllib.parse
import requests
import subprocess
from telegram.ext import Updater
updater = Updater(token='<>', use_context=True)
dispatcher = updater.dispatcher
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
def encrypt_string(hash_string):
    sha_signature = hashlib.sha256(hash_string).hexdigest()
    return sha_signature
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
def textmessage(update, context):
    #context.bot.send_message(chat_id=update.effective_chat.id, text="you said: "+update.message.text)
    utc_time = time.gmtime(time.time())
    ts = time.strftime("%Y-%m-%d %H:%M:%S+00:00 (UTC)", utc_time)
    ts2 = urllib.parse.quote(ts)
    message = update.message.text
    message2 = urllib.parse.quote(message)
    update.message.reply_text('Your message got anchored to the Blockchain. You can do a verification here: \nhttps://ubirch.de/telegram-message-verifier#ts='+ts2+'&id='+str(update.effective_chat.id)+'&data='+message2)
    url="http://pieppiep:8080/1c0996cc-1a4b-45e1-9564-394bc099427f"
    payload = {"data":message,"id":str(update.effective_chat.id),"ts":ts}
    header = {"X-Auth-Token":"<>","Content-Type":"application/json"}
    response = requests.request('POST',url,json=payload,headers=header)
    print(response)
    update.message.reply_text('Status: '+str(response)+' ubirched!')
    print(payload)

def image(update, context):
    user = update.message.from_user
    utc_time = time.gmtime(time.time())
    uts = str(int(time.time()))
    ts = time.strftime("%Y-%m-%d %H:%M:%S+00:00 (UTC)", utc_time)
    ts2 = urllib.parse.quote(ts)
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo_'+str(update.effective_chat.id)+uts+'.jpg')
    python3_command = "/home/pi/ubirch_pybot/ihash.py --interpolation 4 --bits 10 /home/pi/ubirch_pybot/user_photo_"+str(update.effective_chat.id)+uts+".jpg"
    process = subprocess.Popen(python3_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()  # receive output from the python2 script
    imghash1 = str(output)
    imghash = imghash1[2:27]
    time.sleep(5)
    #logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    with open ("user_photo_"+str(update.effective_chat.id)+uts+".jpg", "rb") as img:
     encoded_string=base64.b64encode(img.read())
     hash = encrypt_string(encoded_string)
    update.message.reply_text('Hash of your image is: \n'+imghash+'\nUse it for verification here: \nhttps://ubirch.de/telegram-message-verifier#ts='+ts2+'&id='+str(update.effective_chat.id)+'&data='+imghash+'\nBelow find the sealed image, please download it (after clicking on it) for future checks:')
    img.close()
    time.sleep(10)
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('user_photo_'+str(update.effective_chat.id)+uts+'.jpg', 'rb'))
    url = "http://pieppiep:8080/1c0996cc-1a4b-45e1-9564-394bc099427f"
    #payload = {"data": + hash,"id":+update.effective_chat.id,"ts":+ts}
    payload = {"data":imghash,"id":str(update.effective_chat.id),"ts":ts}
    #payload = {"ts":"2020","data":"67d99970148eff7aefe08396727061fc91b699fe6e2bf69b84fd0574f71d1c56","id":"1069604060"}
    #ubirch it
    header = {"X-Auth-Token":"7b3754a4-f5b2-4d7b-995c-cc0eccd08c93","Content-Type":"application/json"}
    response = requests.request('POST',url,json=payload,headers=header)
    update.message.reply_text('Status: '+str(response)+' ubirched!')
    print(response)
    print(payload)
 


from telegram.ext import MessageHandler, Filters
echo_handler = MessageHandler(Filters.text & (~Filters.command), textmessage)
dispatcher.add_handler(echo_handler)

from telegram.ext import MessageHandler, Filters
image_handler = MessageHandler(Filters.photo, image)
dispatcher.add_handler(image_handler)

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
