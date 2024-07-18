import requests
from config import WEATHER_API_KEY
from googletrans import Translator


def translate_to_english(text):
    translator = Translator()
    translation = translator.translate(text, dest='en')
    return translation.text


def get_weather(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'  # Устанавливаем язык ответа на русский
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        weather_description = data['weather'][0]['description']
        return f"Погода в городе {city}:\nТемпература: {temp}°C\nОписание: {weather_description}"
    else:
        return f"Не удалось получить данные о погоде для {city}. Проверьте название города."

if __name__ == "__main__":
    city = "Москва"
    print(get_weather(city))
