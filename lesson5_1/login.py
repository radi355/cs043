import wsgiref.simple_server
import urllib.parse
import sqlite3

connection = sqlite3.connect('users.db')
cursor = connection.cursor()
connection.execute('CREATE TABLE info (username, password)')

def application(environ, start_response):
    headers = [('Content-Type', 'text/plain; charset=utf-8')]

    path = environ['PATH_INFO']
    params = urllib.parse.parse_qs(environ['QUERY_STRING'])

    if 'username' in params:
        un = params['username'][0]
    else:
        un = None

    if 'password' in params:
        pw = params['password'][0]
    else:
        pw = None

    if path == '/register' and un and pw:

        user = cursor.execute('SELECT * FROM info WHERE username = ?', [un]).fetchall()

        if user:
            start_response('200 OK', headers)
            return ['Sorry, username {} is taken'.format(un).encode()]
        else:
            connection.execute('INSERT INTO info VALUES (?, ?)', [un, pw])
            connection.commit()
            start_response('200 OK', headers)
            return ['Username {} was successfully registered'.format(un).encode()]

    elif path == '/login' and un and pw:
        user = cursor.execute('SELECT * FROM info WHERE username = ? AND password = ?', [un, pw]).fetchall()
        if user:
            start_response('200 OK', headers)
            return ['User {} successfully logged in'.format(un).encode()]
        else:
            start_response('200 OK', headers)
            return ['Incorrect username or password'.encode()]

    else:
        start_response('404 Not Found', headers)
        return ['Status 404: Resource not found'.encode()]

httpd = wsgiref.simple_server.make_server('', 8000, application)
httpd.serve_forever()