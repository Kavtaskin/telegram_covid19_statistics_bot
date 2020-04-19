import telebot
import requests
import re
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver

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
        for i in soup.find('div', class_='covid-stat-view__items'):
            buff.append(i.text.replace(' ', '').replace('\xa0', ''))

        statistic.append('{}{}Статистика COVID19 в РФ по информации на {}:\n\n'.format(emoji_sing,
                                                             emoji_ru_flag,
                                                             re.search(r'[\d]{1,2} [\w]+ 2020', date).group(0)))
        statistic.append('Заражений за всё время: *{}*\n'.format(re.search(r'([\d]+).+', buff[0]).group(1)))
        statistic.append('Заражений за последние сутки: *{}*\n'.format(re.search(r'([\d]+).+ля', buff[1]).group(1)))
        statistic.append('Выздоровлений за всё время: *{}*\n'.format(re.search(r'([\d]+).+здоровлений', buff[2]).group(1)))
        statistic.append('Смертей за всё время: *{}*\n'.format(re.search(r'([\d]+).+мертей', buff[3]).group(1)))
        statistic.append('Проведено тестов: *{}*\n'.format(soup.find('span', class_='covid-panel-view__tests-count').text))

        for i in statistic:
            message += i
        message += '\nПодтверждённые случаи заражений по регионам:\n'

        # get this data by selenium because this data on dynamic page
        driver = webdriver.Chrome()
        sleep(2)
        driver.get(statistic_link)
        sleep(2)
        submit_button = driver.find_element_by_css_selector(".covid-table-view__expand")
        submit_button.click()
        sleep(2)
        data = driver.find_elements_by_class_name("covid-table-view__item")
        for i in data:
            place = i.find_element_by_class_name("covid-table-view__item-name").text.replace('\xa0', '')
            cases = i.find_element_by_class_name("covid-table-view__item-cases").text.replace('\xa0', '')
            diff = i.find_element_by_class_name("covid-table-view__item-cases-diff").text.replace('\xa0', '')
            if diff:
                cities.append(('{}: {} (+{})'.format(place, cases, diff)))
            else:
                cities.append(('{}: {}'.format(place, cases)))
        driver.close()

        for i in cities:
            message += i + '\n'

        message += '\nПодробнее: {}'.format(short_link)

        print(message)

        if data_changed(statistic[1]):
            sleep(30)
            send_message(message)

            write_message(statistic[1])

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
        # check stats every hour
        for i in range(60):
            sleep(60)
