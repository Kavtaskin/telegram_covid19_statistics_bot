import telebot
import requests
import re
from time import sleep
from bs4 import BeautifulSoup

bot = telebot.TeleBot('')

def send_message(message):
    bot.send_message(chat_id='', text=message)

def get_link():
    news_link = 'https://www.rospotrebnadzor.ru/about/info/news/'
    page = requests.get(news_link)
    soup = BeautifulSoup(page.text, 'html.parser')
    if page.status_code == 200:
        covid = soup.find('a', href_='/about/info/news/news_details.php')
        for a in soup.find_all('a', href=True):
            if re.search(r'О подтвержденных случаях новой коронавирусной инфекции COVID-2019 в России', str(a)):
                rpn_link = 'https://www.rospotrebnadzor.ru' + a['href']
                print(rpn_link)
                if data_changed(rpn_link):
                    write_message(rpn_link)
                    get_data(rpn_link)
                break

def get_data(rpn_link):
    page = requests.get(rpn_link)
    soup = BeautifulSoup(page.text, 'html.parser')
    if page.status_code == 200:
        date = soup.find('p', class_='date').text
        emoji = u'\U00002757'
        emoji_flag = u'\U0001F1F7\U0001F1FA'
        date = emoji + date + emoji_flag
        divs1 = soup.findAll(string=re.compile(r'подтвержден.*?[\d]+ '))
        divs_moscow = soup.findAll(string=re.compile(r'[\d]+\. Москва ([\d]+)'))
        divs_rf = soup.findAll(string=re.compile(r'Российской Федерации.+зарегистриров.+ [\d]+ случ.+'))
        moscow = re.search(r'[\d]+\. Москва ([\d]+)', divs_moscow[0])
        moscow_message = 'В том числе {} случаев в Москве'.format(moscow.group(1))
        total = re.search(r'([\d]+)', str(divs_rf[0].split('.')[0]))
        total_message = 'Общее число случаев в РФ: {}'.format(total.group(1))
        more_message = "Подробнее: {}".format(rpn_link)
        message = date + "\n" + divs1[-1] + "\n" + moscow_message + "\n" + total_message + "\n" + more_message
        send_message(message)

def data_changed(message):
    file = open('message.txt', 'r')
    if file.read() == message:
        file.close()
        return False
    else:
        file.close()
        return True

def write_message(message):
    file = open('message.txt', 'w')
    file.write(message)
    file.close()

if __name__ == "__main__":
    while True:
        get_link()
        for i in range(30):
            sleep(60)
            print(i, sep=' ')
