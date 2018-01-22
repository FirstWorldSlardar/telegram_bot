### DATABASE FUNCTIONS ###
import sqlite3
# décorateur
def connect_db(func):
	def connect_do_close(*args, **kwargs):
		conn = sqlite3.connect('sqlite.db')
		cursor = conn.cursor()
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS rdvs (id_chat int PRIMARY KEY, id_message int, txt text)
		''')
		conn.commit()
		kwargs['conn'] = conn
		kwargs['cursor'] = cursor
		values = func(*args, **kwargs)
		conn.commit()
		conn.close()
		return values

	return  connect_do_close

@connect_db
def get_from_sql(requete, conn=None, cursor=None):
	# selection globale
	result_cursor = cursor.execute(requete)
	values = result_cursor.fetchall()
	return values # liste de tuple

@connect_db
def exec_sql(requete, conn=None, cursor=None):
	# simple execution de requête
	cursor.execute(requete)
### 
