import requests
import telebot
from telebot import types

# telebot.apihelper.ENABLE_MIDDLEWARE = True
BOT_TOKEN = ('TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Enter your BTC balance: ')


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Just enter you BTC (only numbers) balance.\n'
                                      'LTC price from nicehash \n'
                                      'UDST to rub price from p2p market on Binance\n'
                                      '/btc to get BTC price\n'
                                      '/ref to get links to nicehash and binance')


@bot.message_handler(commands=['btc'])
def btc_price(message):
    response = requests.get("https://api2.nicehash.com/exchange/api/v2/info/prices")
    data_s = response.json()
    btc_prc = data_s['BTCUSDT']
    bot.send_message(message.chat.id, f'BTC price in USD {btc_prc}')


@bot.message_handler(commands=['ref'])
def buttons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    nicehash = types.KeyboardButton('/Nicehash')
    binance = types.KeyboardButton('/Binance')
    markup.add(nicehash, binance)
    bot.send_message(message.chat.id, "You get it", reply_markup=markup)


@bot.message_handler(commands=['Nicehash', 'Binance'])
def ref_link_one(message):
    markup = types.InlineKeyboardMarkup()
    if message.text == '/Nicehash':
        websitename, weblink = "Nicehash", "https://www.nicehash.com/my/mining/rigs"
    else:
        websitename, weblink = "Binance", "https://www.binance.com/"
    markup.add(types.InlineKeyboardButton(websitename, url=weblink))
    bot.send_message(message.chat.id, 'You welcome', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_user_text(message):
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "p2p.binance.com",
        "Content-Length": "123",
        "Origin": "https://p2p.binance.com",
        "Pragma": "no-cache",
        "TE": "Trailers",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }

    data = {

        "asset": "USDT",
        "fiat": "RUB",
        "merchantCheck": True,
        "page": 1,
        "payTypes": ["TinkoffNew"],
        "publisherType": None,
        "rows": 1,
        "tradeType": "SELL",
        "transAmount": "500"
    }

    sell_get = requests.post("https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search", headers=headers, json=data)
    data_b = sell_get.json()
    if message.text.replace(',', '', 1).replace('.', '', 1).isdigit():
        try:
            btc_balance = float(message.text.replace(',', '.'))
        except ValueError:
            return bot.send_message(message.chat.id, 'Please enter numbers only')
    else:
        return bot.send_message(message.chat.id, 'Please enter numbers only')

    response = requests.get("https://api2.nicehash.com/exchange/api/v2/info/prices")
    data_s = response.json()
    ltc_cur = data_s["LTCBTC"]
    usdt_ltc = data_s["LTCUSDT"]
    ltc_balance = ((btc_balance / ltc_cur) - ((btc_balance / ltc_cur) * 0.004)) - 0.00002
    p2p_usdt_rub = data_b['data'][0]['adv']['price']
    rub_balance = '%.2f' % eval(f'{ltc_balance}*{usdt_ltc}*{p2p_usdt_rub}')
    bot.send_message(message.chat.id,
                     f" LTC to BTC = {ltc_cur}\nLTC Balance = {'%.5f' % ltc_balance}\n"
                     f"LTC to USD = {usdt_ltc}\nP2P USDT to RUB = {p2p_usdt_rub}\nYour income = {rub_balance} RUB")


bot.polling(none_stop=True)
