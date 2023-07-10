import requests
import telebot
from telebot import types

# telebot.apihelper.ENABLE_MIDDLEWARE = True
BOT_TOKEN = ('TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

HEADERS = {
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

DATA = {

    "asset": "USDT",
    "fiat": "RUB",
    "merchantCheck": True,
    "page": 1,
    "payTypes": ["TinkoffNew"],
    "publisherType": None,
    "rows": 1,
    "tradeType": "SELL",
    "transAmount": "5000"
}

def get_currency_nicehash():
    get_json = requests.get("https://api2.nicehash.com/exchange/api/v2/info/prices").json()
    return {'BTCUSDT':get_json['BTCUSDT'], "LTCBTC":get_json["LTCBTC"], "LTCUSDT":get_json["LTCUSDT"]}


def get_currency_binance():
    return requests.post("https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search",
                         headers=HEADERS, json=DATA).json()['data'][0]['adv']['price']

def count_currecy(btc_balance):
    currencies = get_currency_nicehash()
    ltc_cur, usdt_cur = currencies["LTCBTC"], currencies["LTCUSDT"]
    ltc_balance = ((btc_balance / ltc_cur) - ((btc_balance / ltc_cur) * 0.004)) - 0.00002
    p2p_usdt_rub = float(get_currency_binance())
    rub_balance = ltc_balance * usdt_cur * p2p_usdt_rub
    return ltc_cur, ltc_balance, usdt_cur, p2p_usdt_rub, rub_balance


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Enter your BTC balance: ')


@bot.message_handler(commands=['help'])
def help_(message):
    bot.send_message(message.chat.id, 'Just enter you BTC (only numbers) balance.\n'
                                      'LTC price from nicehash \n'
                                      'USDT to rub price from p2p market on Binance\n'
                                      '/btc to get BTC price\n'
                                      '/ref to get links to nicehash and binance\n'
                                      '/rub to get USDT price from binance')


@bot.message_handler(commands=['btc'])
def btc_price(message):
    btc_prc = get_currency_nicehash()['BTCUSDT']
    bot.send_message(message.chat.id, f'BTC price in USD {btc_prc}')


@bot.message_handler(commands=['rub'])
def p2p_rub(message):
    usd_rub = get_currency_binance()
    bot.send_message(message.chat.id, f'USDT is sold at price {usd_rub}')


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
    site_names = { '/Nicehash': ("Nicehash", "https://www.nicehash.com/my/mining/rigs"),
                   "/Binance": ("Binance", "https://www.binance.com/") }
    markup.add(types.InlineKeyboardButton(site_names[message.text][0], url=site_names[message.text][1]))
    bot.send_message(message.chat.id, 'You welcome', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def btc_balance_to_rub(message):
    try:
        btc_balance = float(message.text.replace(',', '.', 1))
    except ValueError:
        return bot.send_message(message.chat.id, 'Please enter numbers only')
    ltc_cur, ltc_balance, usdt_cur, p2p_usdt_rub, rub_balance = count_currecy(btc_balance)
    bot.send_message(message.chat.id,
                     f"LTC to BTC = {ltc_cur}\nLTC Balance = {ltc_balance:.5f}\n"
                     f"LTC to USD = {usdt_cur}\nP2P USDT to RUB = {p2p_usdt_rub}\nYour income = {rub_balance:.2f} RUB")


bot.polling(none_stop=True)