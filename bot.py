import telebot
import requests
import re
from time import sleep
from bs4 import BeautifulSoup

emoji_sing = u'\U00002757'
emoji_ru_flag = u'\U0001F1F7\U0001F1FA'
short_link = 'https://yandex.ru/maps/covid19'
statistic_link = 'https://yandex.ru/maps/covid19?ll=41.775580%2C54.894027&z=3'
statistic = []
buff = []
cities = []

def send_message(message):
    bot = telebot.TeleBot(get_info('token.txt'))
    bot.send_message(chat_id=get_info('chat_id.txt'), text=message, parse_mode= "Markdown")

def check_statistics():
    message = ''
    page = requests.get(statistic_link)
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, 'html.parser')
        date = emoji_sing + soup.find('div', class_='covid-panel-view__subtitle').text + emoji_ru_flag + '\n'
        for i in soup.find('div', class_='covid-panel-view__stat-items _even'):
            buff.append(i.text.replace(' ', '').replace('\xa0', ''))

        statistic.append('{}{}Статистика COVID19 в РФ по информации на {}:\n\n'.format(emoji_sing,
                                                             emoji_ru_flag,
                                                             re.search(r'[\d]{1,2} [\w]+ 2020', date).group(0)))
        statistic.append('Заражений за всё время: *{}*\n'.format(re.search(r'([\d]+).+завсёвремя', buff[0]).group(1)))
        statistic.append('Заражений за последние сутки: *{}*\n'.format(re.search(r'\+([\d]+).+за[\d]{1,2}', buff[1]).group(1)))
        statistic.append('Выздоровлений за всё время: *{}*\n'.format(re.search(r'([\d]+).+здоровлений', buff[2]).group(1)))
        statistic.append('Смертей за всё время: *{}*\n'.format(re.search(r'([\d]+).+мертей', buff[3]).group(1)))

        for i in statistic:
            message += i
        message += '\nПодтверждённые случаи заражений по регионам:\n'

        for i in soup.find('div', class_='covid-panel-view__items'):
            city = re.findall(r'([\D\W]+)([\d ]+)\+?(\+?[\d]+)?', i.text.replace('\xa0', ''))
            if city[0][1] != ' ':
                 if city[0][2] != '':
                     cities.append(('{}: {} (+{})'.format(city[0][0], city[0][1], city[0][2])))
                 else:
                     cities.append('{}: {}'.format(city[0][0], city[0][1]))
        for i in cities:
            message += i + '\n'
        message += 'Подробнее: {}'.format(short_link)
        if data_changed(message):
            print(message)
            send_message(message)
            write_message(message)

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

def get_info(data):
    file = open(data, 'r')
    info = file.read()
    file.close()
    return info

if __name__ == "__main__":
    while True:
        check_statistics()
        for i in range(60):
            sleep(60)
            print(i, sep=' ')
