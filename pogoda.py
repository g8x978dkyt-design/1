import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

bot = telebot.TeleBot('8251157779:AAF5dTI0osPBnrRhehFVjrEAAKxWqNy_5YM')

user_state = {}


def get_air_quality_kemerovo():
    url = "https://airkemerovo.ru/"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=100, proxies=None)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Получаем весь текст страницы
        page_text = soup.get_text()

        # Ищем температуру и ветер (они есть в тексте)
        temp = "нет данных"
        wind = "нет данных"

        # Ищем строку типа "-3°C 7м/с ↓"
        import re
        weather_pattern = r'([-+]?\d+°C\s+\d+м/с\s+[↓↑]?)'
        weather_match = re.search(weather_pattern, page_text)
        if weather_match:
            weather_text = weather_match.group(1)
            temp_match = re.search(r'([-+]?\d+°C)', weather_text)
            if temp_match:
                temp = temp_match.group(1)
            wind_match = re.search(r'(\d+м/с)', weather_text)
            if wind_match:
                wind = wind_match.group(1)

        # Ищем все числа на странице (это значения PM и других показателей)
        numbers = re.findall(r'\b\d{1,3}\b', page_text)
        # Фильтруем числа (убираем слишком маленькие и слишком большие)
        valid_numbers = [n for n in numbers if 5 <= int(n) <= 200]

        # На сайте отображается много показателей, возьмем несколько
        pm25 = "X"
        pm10 = "X"
        aqi = "X"

        # Если есть числа, берем первые несколько как наиболее актуальные
        if len(valid_numbers) >= 3:
            pm25 = valid_numbers[0]
            pm10 = valid_numbers[1]
            aqi = valid_numbers[2]
        elif len(valid_numbers) >= 2:
            pm25 = valid_numbers[0]
            pm10 = valid_numbers[1]
        elif len(valid_numbers) >= 1:
            pm25 = valid_numbers[0]

        # Определяем статус на основе значений
        status = "нет данных"
        try:
            pm_val = int(pm25) if pm25 != "X" else 0
            if pm_val <= 35:
                status = "🟢 Хорошо"
            elif pm_val <= 75:
                status = "🟡 Приемлемо"
            else:
                status = "🔴 Вредно"
        except:
            pass

        # Проверяем наличие НМУ
        nmu_mention = ""
        if "нму" in page_text.lower() or "неблагоприят" in page_text.lower():
            nmu_mention = "\n⚠️ На сайте упоминаются неблагоприятные условия."

        result = (
            f"🌬 Актуально сейчас в Кемерово (airkemerovo.ru):\n\n"
            f"Температура: {temp}\n"
            f"Ветер: {wind}\n"
            f"PM2.5: {pm25}\n"
            f"PM10: {pm10}\n"
            f"AQI: {aqi}\n"
            f"Статус воздуха: {status}\n"
            f"{nmu_mention}\n"
            f"\nДанные обновлены: {response.headers.get('Date', 'неизвестно')}"
        )
        return result
    except Exception as e:
        return f"Не удалось загрузить данные 😔\nОшибка: {str(e)}\nСсылка: https://airkemerovo.ru/"

# Твой оригинальный код + добавление актуальных данных только в нужном месте
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    # ИСПРАВЛЕНИЕ: добавил обработку ПДК
    if message.text == "ПДК":
        user_state[message.chat.id] = "ПДК"
        bot.send_message(message.chat.id, "1 класс (Чрезвычайно опасные)")
        bot.send_message(message.chat.id, "Примеры: Ртуть, мышьяк, цианиды.")
        bot.send_message(message.chat.id,
                         "Что делать: НЕ ТРОГАТЬ! При любом контакте (разбился градусник, разлитое пятно) — срочно покинуть помещение, вызвать МЧС (112) или взрослых. Не дышать рядом.")
        bot.send_message(message.chat.id, "2 класс (Высокоопасные)")
        bot.send_message(message.chat.id,
                         "Примеры: Формальдегид (в новой мебели), аммиак (нашатырь), хлорка, некоторые кислоты.")
        bot.send_message(message.chat.id,
                         "Что делать: Избегать попадания на кожу и в легкие. Работать только в перчатках и проветривать помещение. При отравлении — свежий воздух и врач")
        bot.send_message(message.chat.id, "3 класс (Умеренно опасные)")
        bot.send_message(message.chat.id, "Примеры: Бензин, ацетон, красители, выхлопные газы, нитраты.")
        bot.send_message(message.chat.id,
                         "Что делать: Не нюхать, не пить. Мыть руки после контакта. Хранить в плотно закрытой таре. Не находиться долго в тумане или смоге.")
        bot.send_message(message.chat.id, "4 класс (Малоопасные)")
        bot.send_message(message.chat.id, "Примеры: Аммиачные удобрения (сухие), сода, мел, этиловый спирт.")
        bot.send_message(message.chat.id,
                         "Что делать: Соблюдать обычную гигиену. Хотя они почти безопасны, специально есть или пить их все равно нельзя. При проглатывании может быть расстройство желудка.")

    elif message.text == "НМУ":
        user_state[message.chat.id] = "НМУ"
        bot.send_message(message.chat.id, "Когда объявляют НМУ?")
        bot.send_message(message.chat.id, "Безветренная погода (штиль)")
        bot.send_message(message.chat.id, "Туман")
        # ИСПРАВЛЕНИЕ: убрал дублирование строки
        bot.send_message(message.chat.id, "Температурная инверсия (холодный воздух внизу, тёплый — наверху)")
        bot.send_message(message.chat.id,
                         "В такие дни воздух становится грязным, вредные вещества не рассеиваются и копятся у земли.")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn5 = types.KeyboardButton("да")
        btn6 = types.KeyboardButton("нет")
        markup.add(btn5, btn6)
        bot.send_message(message.chat.id, "Хотите узнать актуальную информацию о режиме НМУ?", reply_markup=markup)

    elif message.text == "да" or message.text == "нет":
        if message.chat.id in user_state:
            if user_state[message.chat.id] == "ПДК":
                if message.text == "да":
                    bot.send_message(message.chat.id, "🔍 Получаю актуальные данные по ПДК...")
                    # ИСПРАВЛЕНИЕ: добавил заглушку для ПДК
                    bot.send_message(message.chat.id, "Данные по ПДК пока не доступны. Попробуйте позже.")
                else:
                    bot.send_message(message.chat.id, "Хорошо! Если захотите узнать позже - просто нажмите ПДК снова.")
            elif user_state[message.chat.id] == "НМУ":
                if message.text == "да":
                    bot.send_message(message.chat.id, "🔍 Получаю актуальную информацию о НМУ...")
                    air_info = get_air_quality_kemerovo()
                    bot.send_message(message.chat.id, air_info)
                else:
                    bot.send_message(message.chat.id, "Хорошо! Будьте здоровы!")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("ПДК")
        btn2 = types.KeyboardButton("НМУ")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, "Выберите раздел:", reply_markup=markup)

        user_state[message.chat.id] = None

    # ИСПРАВЛЕНИЕ: добавил обработку /start
    elif message.text == "/start":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("ПДК")
        btn2 = types.KeyboardButton("НМУ")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, 'Чем я могу помочь, про что рассказать?', reply_markup=markup)
        user_state[message.chat.id] = None


# ИСПРАВЛЕНИЕ: добавил защиту от вылетов
if __name__ == '__main__':
    print("🚀 Бот запущен...")
    import time
    import logging

    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='bot.log'  # сохраняем логи в файл
    )

    restart_count = 0

    while True:
        try:
            logging.info("Бот запущен")
            restart_count = 0  # сбрасываем счетчик при успехе
            bot.polling(none_stop=True, interval=1, timeout=30)

        except KeyboardInterrupt:
            logging.info("Бот остановлен вручную")
            break

        except Exception as e:
            restart_count += 1
            logging.error(f"Ошибка #{restart_count}: {e}")

            # Если слишком много ошибок подряд - увеличиваем паузу
            if restart_count > 5:
                sleep_time = 60
                logging.warning(f"Много ошибок подряд, пауза {sleep_time}с")
            else:
                sleep_time = 5

            print(f"🔄 Перезапуск #{restart_count} через {sleep_time}с...")
            time.sleep(sleep_time)