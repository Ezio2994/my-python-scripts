import decimal

from bs4 import BeautifulSoup
import requests
import re
from decimal import Decimal
from forex_python.converter import CurrencyRates, CurrencyCodes, RatesNotAvailableError
import xlsxwriter
from datetime import datetime
import threading


c = CurrencyRates()
cd = CurrencyCodes()


cryptos = {}


def generate_prices():
    url = requests.get("https://coinmarketcap.com/").text
    parsed_page = BeautifulSoup(url, "html.parser")

    tbody = parsed_page.tbody
    trs = tbody.findAll("tr")

    i = 0

    for tr in trs:
        if i < 10:
            name = tr.find("p", class_="sc-1eb5slv-0 iworPT").string
            price = tr.find("a", class_="cmc-link", text=re.compile(r"\$.*")).string
            currency_code = tr.find("p", class_="sc-1eb5slv-0 gGIpIK coin-item-symbol").string

            cryptos[name] = (currency_code, price)

            i = i + 1
        else:
            spans = tr.findAll("span")
            this_name = spans[3].string
            this_price = tr.findAll("td")[3].contents[0].text
            this_currency_code = tr.findAll("span")[4].string

            cryptos[this_name] = (this_currency_code, this_price)


generate_prices()


what_user_wanna_see = input("What would you like to see? \n 1) List of all coin with price \n 2) Specific coin with "
                            "different currency and amount to buy \n 3) Create an exel file with the price variation"
                            " over time")

if what_user_wanna_see == "1":
    how_to_sort = input("How do you want the list to be sort? \n 1) Rank (default) \n 2) Price")
    cryptos_list = list(cryptos.items())

    def sorting_func(this_crypto):
        return Decimal(re.sub(r'[^\d.]', '', this_crypto[1][1]))

    if how_to_sort == "2":
        cryptos_list = sorted(cryptos_list, key=sorting_func, reverse=True)

    for crypto in cryptos_list:
        print(f"{crypto[0]}({crypto[1][0]}): {crypto[1][1]}")

elif what_user_wanna_see == "2":
    whichCoin = input("Which coin?")
    whichCurrency = input("Which currency? if omit is gonna be GBP")
    amount = input("How much of the selected currency would you like to buy?")

    def find_name(this_crypto):
        if whichCoin.lower() == this_crypto.lower():
            return True
        else:
            return False

    try:
        whichCoin = list(filter(find_name, cryptos.keys()))[0]

        if len(whichCurrency) == 0:
            whichCurrency = "GBP"

        symbol = cd.get_symbol(whichCurrency)
        crypto_symbol = cd.get_symbol(cryptos[whichCoin][0])

        if crypto_symbol is None:
            crypto_symbol = " " + cryptos[whichCoin][0]

        toNumber = Decimal(re.sub(r'[^\d.]', '', cryptos[whichCoin][1]))
        result = c.convert("USD", whichCurrency, toNumber)

        if len(amount) == 0:
            amount = 0

        percentage = (int(amount) / result) * 100
        message_rest = ""

        if amount != 0:
            message_rest = f" and with {symbol + amount} you could buy" \
                           f" {'{0:,.3f}'.format(percentage / 100)}{crypto_symbol}"

        print(f"The price of {whichCoin} is {cryptos[whichCoin][1]} which in {whichCurrency} is "
              f"{symbol + '{0:,.2f}'.format(result)}" + message_rest)

    except (KeyError, IndexError):
        print("No such coin found")
    except RatesNotAvailableError:
        print("rate not available")
    except ValueError:
        print(amount + " is not a number")
    except decimal.DivisionByZero:
        print(whichCoin + " price is too low for this program to give you data")

elif what_user_wanna_see == "3":
    howLong = input("Every how many minutes do you wish to save the current price and see the difference compare to last one?")
    workbook = xlsxwriter.Workbook(f"cryptos {datetime.today()}.xlsx")
    worksheet = workbook.add_worksheet()

    def to_number(number):
        return Decimal(re.sub(r'[^\d.]', '', number))

    prev_price = {}

    def keep_loop(e):
        row = 1
        col = 1
        worksheet.set_row(0, None, workbook.add_format({"fg_color": "silver", "align": "center"}))

        while not e.is_set():
            generate_prices()

            centered = workbook.add_format({"align": "center"})

            worksheet.write(0, 0, 'Name')
            worksheet.set_column(0, 0, 20)
            worksheet.write(0, col, "Price " + datetime.today().strftime("%X"))
            worksheet.set_column(col, col, 20, centered)

            if col > 1:
                worksheet.write(0, col - 1, "Difference")
                worksheet.set_column(col - 1, col - 1, 10, centered)

            for name, price in list(cryptos.items()):
                if name in prev_price:
                    difference = to_number(price[1]) - to_number(prev_price[name])
                    is_first = 2 if col == 3 else col - 1

                    if difference > 0:
                        this_format = workbook.add_format({"font_color": "green", "align": "center"})
                        worksheet.write(row, is_first, "+$" + str(difference), this_format)
                    elif difference < 0:
                        this_format = workbook.add_format({"font_color": "red", "align": "center"})
                        worksheet.write(row, is_first, str(difference)[0] + "$" + str(difference)[1:], this_format)
                    else:
                        worksheet.write(row, is_first, str(difference))

                prev_price[name] = price[1]
                worksheet.write(row, 0, name)
                worksheet.write(row, col, price[1])
                row += 1

            row = 1
            col += 2
            print("collected data" + str(datetime.now().strftime("%X")))
            e.wait(int(howLong) * 60)

    event = threading.Event()

    main_thread = threading.Thread(name='main program', target=keep_loop, args=[event])
    main_thread.start()

    while True:
        print("Write 'stop' to stop recording data and generate exel file ")
        if input().lower() == 'stop':
            workbook.close()
            print('Program terminated and pdf generated')
            event.set()
            break

    main_thread.join()

else:
    print("No such option")
