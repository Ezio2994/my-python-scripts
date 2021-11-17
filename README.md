# my-python-scripts

## crypto-web-scraping

I've usued BeautifulSoup and requests modules to get some crypo datas from https://coinmarketcap.com/ and used them to give the user the option to view the datas in different way. <br>

With option one user could see a list of 100 popular cryptocurrencies and sort them by rank or price from high to low. <br>
I used modules Decimal and re to format price string to a price number so could easily use sorted() to sort the numbers.

With option two user can choose what crypto to get, which currency to convert the price from USD and how much of the selected coin could buy with the selected currency. <br>
I wrote a function that through filter() find the intended coin ignoring case sensitive, used forex_python.converter to do the currency exchange and used a mathematical formula to give the user the buyable amount. <br>

With option 3 user can get a exel file with the value of the coin every tot minutes with the difference between the 2 values. <br>
Used xlsxwriter to generate the exel file and threading so that I could eventually get the input from the user to stop the program while the 'while loop' is keeping generating the exel file.
