import mysql.connector

mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	passwd="1234",
	auth_plugin='mysql_native_password')

my_cursor = mydb.cursor()

#my_cursor.execute("Create DATABASE our_users")

my_cursor.execute("show databases")
for db in my_cursor:
	print(db)