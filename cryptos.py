import urllib3
urllib3.disable_warnings() 
# we just request the coinmarket API, so sensible
# data exchanged here
import json
from db_functions import get_from_sql, exec_sql
import matplotlib.pyplot as plt


def getCurrency(currency_name):
	"""
	returns:  
    {
        "id": "siacoin", 
        "name": "Siacoin", 
        "symbol": "SC", 
        "rank": "29", 
        "price_usd": "0.0394902", 
        "price_btc": "0.00000357", 
        "24h_volume_usd": "34550600.0", 
        "market_cap_usd": "1239840092.0", 
        "available_supply": "31396146174.0", 
        "total_supply": "31396146174.0", 
        "max_supply": null, 
        "percent_change_1h": "0.21", 
        "percent_change_24h": "-3.88", 
        "percent_change_7d": "-11.05", 
        "last_updated": "1516815848"
    }
	"""

	http = urllib3.PoolManager()
	r = http.request("GET", "https://api.coinmarketcap.com/v1/ticker/%s/" % (currency_name,))
	currency_dic = json.loads(r.data.decode("utf-8"))[0]
	return currency_dic


def getSummary(currency_name):
	all_data = getCurrency(currency_name)
	dic = {
		"name": all_data['name'],
		"price_usd": all_data['price_usd'],
		"market_cap_usd": all_data['market_cap_usd'],
		"percent_change_24h": all_data['percent_change_24h']
	}
	return dic


def simplify_numbers(float_number_string_us):
	split = float_number_string_us.split('.')
	# [integer, floatting_value]
	integer_list = [c for c in split[0]] # -> list
	# we add ',' for every 3 digits
	n_digits = len(integer_list)
	for i in range(1,n_digits+1):
		if i%3==0 and (n_digits-i) != 0:
			integer_list.insert(n_digits-i, ',')

	try :
		return ''.join(integer_list)+'.'+split[1]
	except IndexError as e:
		return ''.join(integer_list)


def returnSummary(typeLimit, currency_name, limit):
	s = getSummary(currency_name)
	if typeLimit=="down":
		text = "est tombé sous"
	else:
		text = "a dépassé"
	return """ {0} {1} votre limite ${2:.3g}\n 
		Prix : ${3:.3g} \n
		Variation journalière: {4}%\n
		Market Cap: ${5}
		""".format(s['name'], text, limit, float(s['price_usd']), s['percent_change_24h'], simplify_numbers(s['market_cap_usd']))


def check_up(currency_name, limit):
	price = float(getCurrency(currency_name)['price_usd'])
	if price >= limit:
		return True
	return False


def check_down(currency_name, limit):
	price = float(getCurrency(currency_name)['price_usd'])
	if price <= limit:
		return True
	return False


def check_cryptos(bot, job):
	"""
	params: bot et job sont obligatoires car cette function
	callback est appelée dans jobQueue.run_repeating()
	"""
	results = get_from_sql("SELECT id_chat, type, currency, value FROM cryptos")
	for currencyLimit in results:
		id_chat, typeLimit, currency, limit = currencyLimit
		summary = returnSummary(typeLimit, currency, limit)
		if typeLimit=="down":
			if check_down(currency, limit):
				bot.send_message(chat_id=id_chat, text=summary)
		else:
			if check_up(currency, limit):
				bot.send_message(chat_id=id_chat, text=summary)


def generateHoldingsImg(id_chat):
	holdings = get_from_sql("SELECT currency, tokens FROM holdings WHERE id_chat=%d" % id_chat)
	labels = []
	sizes = []
	total_value, maximum, i_max, i = 0, 0, 0, 0
	for currency_holding in holdings:
		currency, tokens = currency_holding
		tokens_value = tokens*float(getSummary(currency)["price_usd"])
		if tokens_value >= maximum:
			maximum = tokens_value
			i_max = i 
		labels.append(currency)
		sizes.append(tokens_value)
		total_value += tokens_value
		i +=1
	values = sizes
	sizes = [value/total_value for value in sizes]
	explode = [0 if j!=i_max else 0.1 for j in range(len(labels))]
	
	fig1, ax1 = plt.subplots(figsize=(2.5,1.5)) # (w, h) in inches
	ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
	        shadow=True, startangle=90)
	ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
	fig1.savefig('pie.png')
	return total_value, labels, values
