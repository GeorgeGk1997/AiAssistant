import cv2
import numpy as np
import pickle, os, sqlite3, random
import datetime
from datetime import datetime as dt


'''
CREATE TABLE "users" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"username"	TEXT NOT NULL UNIQUE,
	"name"	TEXT,
	"surname"	TEXT,
	"address"	TEXT,
	"infected_date"	TEXT DEFAULT 'healthy'
);

'''
class Users_DB:

	conn = None
	def __init__(self):
		if os.path.exists("users_asis.db"):
			self.conn = sqlite3.connect("users_asis.db")
			print("Successful connection with database")

	def add_user(self, username, name, surname, address, inserted = False):
		conn = sqlite3.connect("users_asis.db")
		while True:
			command = "INSERT INTO users (username, name, surname, address) VALUES (\'%s\',\'%s\', \'%s\', \'%s\')" % (username.lower(), name, surname, address)
			try:
				conn.execute(command)
				inserted = True
				print("inserted")
			except sqlite3.IntegrityError:
				username = input("This username exists! Give another one.")
			conn.commit()
			if(inserted):
				break

	def change_username(self, old_username, new_username):
		select_string = "SELECT id FROM users WHERE username == \'%s\'" % old_username

		conn = sqlite3.connect("users_asis.db")
		cursor = conn.cursor()
		cursor.execute(select_string)
		rows = cursor.fetchall()

		for row in rows:
			users_id = row[0]
			command = "UPDATE users SET username = \'%s\' WHERE id = %s" % (new_username, users_id)
			try:
				conn.execute(command)
				print("inserted")
			except sqlite3.Error as er:
				print("Error: "+str(er))
			conn.commit()

	def change_address(self, username, address):
		select_string = "SELECT id FROM users WHERE username == \'%s\'" % username

		conn = sqlite3.connect("users_asis.db")
		cursor = conn.cursor()
		cursor.execute(select_string)
		rows = cursor.fetchall()

		for row in rows:
			users_id = row[0]
			command = "UPDATE users SET address = \'%s\' WHERE id = %s" % (address, users_id)
			try:
				conn.execute(command)
				print("inserted")
			except sqlite3.Error as er:
				print("Error: "+str(er))
			conn.commit()

	def user_got_infected(self, username):
		day_of_infection = dt.today().strftime('%Y-%m-%d')
		command = "UPDATE users SET infected_date = \'%s\' WHERE username = \'%s\'" % (str(day_of_infection), username)
		try:
			self.conn.execute(command)
			print("Successful")
		except sqlite3.Error as er:
			print("Error: " + str(er))
		self.conn.commit()

	def user_cured(self, username):
		day_of_infection = dt.today().strftime('%Y-%m-%d')
		command = "UPDATE users SET infected_date = \'%s\' WHERE username = \'%s\'" % ("healthy", username)
		try:
			self.conn.execute(command)
			print("Successful")
		except sqlite3.Error as er:
			print("Error: " + str(er))
		self.conn.commit()



	def user_data(self, username):
		select_string = "SELECT * FROM users WHERE username == \'%s\'" % username
		cursor = self.conn.cursor()
		cursor.execute(select_string)
		rows = cursor.fetchall()

		for row in rows:
			#0: user_id | 1: username | 2: name 
			#3: surname | 4: address | 5: infected_date 
			return row[2],row[3],row[4],row[5]






# obj = Users_DB()
# name,surname,addr,infected=obj.user_data("iqmma")
# print(name, surname, addr, infected)
# obj.add_user("Georgegdk","George", "Gkourlias", "Acharnes")
# obj.change_username("whatever", "iqmma")
# obj.change_address("iqmma","menidi")

#today date -> datetime.today().strftime('%Y-%m-%d')
# delta = kvr -gvr
# print(dt.today().strftime('%Y-%m-%d'))
#G. Gkourlias