import sqlite3

connection = sqlite3.connect('business.db')

cursor = connection.cursor()

products = cursor.execute('SELECT prodname, weight FROM products').fetchall()

for pname, weight in products:
    print('Product: {}\tWeight: {} kg'.format(pname, weight))

