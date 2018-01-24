import urllib3
import json
from db_functions import get_from_sql, exec_sql


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


def returnSummary(typeLimit, currency_name, limit):
	s = getSummary(currency_name)
	if typeLimit=="down":
		text = "est tombé sous"
	else:
		text = "a dépassé"
	return """ {0} {1} votre limite ({2})\n 
		Prix : {3} \n
		Variation journalière: {4}%\n
		Market Cap: {5}
		""".format(s['name'], text, limit, s['price_usd'], s['percent_change_24h'], s['market_cap_usd'])


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
				job.interval *= 10
		else:
			if check_up(currency, limit):
				bot.send_message(chat_id=id_chat, text=summary)
				job.interval *= 10

