import time
import hashlib
import requests
import json
import telegram
import urllib.parse
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
# ___________________________________________________ CONFIG AREA _____________________________________________________________

# This will prevent sending messages to channel during development
debug = True
# Time  delay it will wake and and check....
sleep_time =300 #seconds

server_url = ""
bot = None
CHANNEL_ID = ""
PRIVATE_ID = ""


quick_notification_link = "https://t.me/KTU_RC/14"
add_url = "https://ktu.edu.in"
url = "https://ktu.edu.in/eu/core/announcements.htm"

# Header footer shown for whatsapp link
header = " 📢 New *KTU* Notification: \n"
footer2 =  ".\n ------------------------- \n  Countinue reading: *KTU Notification Channel* \n  👉 Join Now!  https://t.me/KTU_RC  \n *Share to your friends* "

# Footer shown for Other messages
footer =  "\n ------------------------- \n "

# ------------------------------------------------------END OF CONFIG------------------------------------------------------

# todo : Implemnt a error detection and report system
error_val = ""

def log(message):
    print(message)

def getlist():
    with urllib.request.urlopen(server_url) as url:
        data = json.loads(url.read().decode())
        if data is None:
            bot.send_message(chat_id=PRIVATE_ID, text="*Read From DB Failed*", disable_notification=False,
                         parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
            exit(1)
        return data

def save_msg_hash(listi):
    if listi != None:
        sll = requests.put(server_url ,json=listi)
        if sll.status_code is not 200:
            bot.send_message(chat_id=PRIVATE_ID, text="*Write to DB Failed* : `" + str(sll.status_code )+ "`", disable_notification=False,
                         parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)

def remove_last(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def build_menu(buttons, n_cols):
    menu = [buttons[sd:sd + n_cols] for sd in range(0, len(buttons), n_cols)]
    return menu

def send_notification(notification, link_list4):
    if debug:
        bot.send_message(chat_id=PRIVATE_ID, text= notification,
                     reply_markup=InlineKeyboardMarkup(build_menu(link_list4, n_cols=2)),
                     disable_web_page_preview=True, parse_mode=telegram.ParseMode.MARKDOWN)
    if not debug:
        bot.send_message(chat_id=CHANNEL_ID , text=notification, parse_mode=telegram.ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup(build_menu(link_list4, n_cols=2)),
                        disable_web_page_preview=True)
    log("Message Sent")

def find_links(links, body):
    link_list = [InlineKeyboardButton("Quick Navigation Panel", url=quick_notification_link)]
    for link in links:
        body = remove_last(body, link.text, "", 1)
        if "ktu.edu" in link["href"]:
            temp_link = link["href"]
        else:
            temp_link = add_url + link["href"]
        link_list.append(InlineKeyboardButton(link.text, url=temp_link))
    return body,link_list

def main_function():
    msg_list = []
    hash_list = getlist()
    log("Connecting to website")
    try:
        website = requests.get(url).text
    except:
        print("Unable to access Website!")
        bot.send_message(chat_id=PRIVATE_ID, text="*Unable to accesss Website*", disable_notification=False,
                         parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    if "Page Not Found" in website:
        log("Page not found")
        bot.send_message(chat_id=PRIVATE_ID, text="*Unable to accesss Website*", disable_notification=False,
                         parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
        exit(2)
    else:
        log("Connected Successfully")

    soup = BeautifulSoup(website, 'html.parser')
    all_notification = soup.findAll('tr')

    i = 0
    for item in all_notification:
        contents = item.findAll('li')
        heading_temp = item.findAll('b')
        heading = "*" + heading_temp[1].text + "* \n\n"
        body = (str(contents[0].text).split(heading_temp[1].text))[1]
        body , links = find_links(item.findAll('a', href=True), body=body)
        body = " ".join(body.split())
        links.append(InlineKeyboardButton("WhatsApp It!", "https://api.whatsapp.com/send?&text=" + urllib.parse.quote(
            header + heading + body + footer2)))
    
        if i < 5:
            msg_hash = (hashlib.md5(heading.encode('utf-8')).hexdigest())
            msg_list.append(msg_hash)
            if not msg_hash in hash_list:
                send_notification(heading + body + footer, links)
            if debug:
                send_notification(heading + body + footer, links)
        else:
            break
        i = i + 1
    if not debug:
        save_msg_hash(msg_list)
    else:
        choice = input("Save List to DB?(y/n)")
        if choice is "y":
            save_msg_hash(msg_list)


def main():
    if not debug:
        print("Intialising varibles:")
        with open('secure.json') as json_file:  
            data = json.load(json_file)
            global bot 
            bot = telegram.Bot(token=data['bot_token'])
            global server_url
            server_url = data['server_url']
            global PRIVATE_ID
            PRIVATE_ID = data['priv_id']
            global CHANNEL_ID
            CHANNEL_ID = data['channel_id']
    else:
        print("Debug mode")
        if bot is None or server_url is "" or CHANNEL_ID is "" or PRIVATE_ID is "":
            print("You must Initialise the variables bot,server_url,CHANNEL_ID,PRIVATE_ID")
            exit(1)
    log("System Initialised..")

    global error_val

    if not debug:
        while True:
            try:
                main_function()
                log("Going to sleep")
                time.sleep(sleep_time)
                error_val = ""
                log("Waking from sleep")
            except Exception as e:
                try:
                    bot.send_message(chat_id=PRIVATE_ID, text="*Error* : `" + e + "`", disable_notification=False,
                         parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
                except e:
                    pass
                
                print("Exception Occurred:" + str(e))
                log(e)
                time.sleep(sleep_time)
    else:
        main_function()

if __name__ == '__main__':
    main()

