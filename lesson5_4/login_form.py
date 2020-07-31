import wsgiref.simple_server
import urllib.parse
import sqlite3

connection = sqlite3.connect('users.db')
cursor = connection.cursor()
connection.execute('CREATE TABLE info (username, password)')


def application(environ, start_response):
    headers = [('Content-Type', 'text/html; charset=utf-8')]
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
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            start_response('200 OK', headers)
            returnregister = '<p><a href="/account">View account status</a></p>'
            return ['User {} was successfully registered'.format(un).encode() + returnregister.encode()]


    elif path == '/login' and un and pw:
        user = cursor.execute('SELECT * FROM info WHERE username = ? AND password = ?', [un, pw]).fetchall()
        if user:
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            start_response('200 OK', headers)
            returnlogin = '<p><a href="/account">View account status</a></p>'
            return ['User {} successfully logged in'.format(un).encode() + returnlogin.encode()]
        else:
            start_response('200 OK', headers)
            return ['Incorrect username or password'.encode()]

    elif path == '/logout':
        headers.append(('Set-Cookie', 'session=0; expires=Thu, 01 Jan 1970 00:00:00 GMT'))
        start_response('200 OK', headers)
        login = '<p><a href="/">Log in again</a></p>'
        return ['Logged out'.encode() + login.encode()]

    elif path == '/account':
        start_response('200 OK', headers)
        if 'HTTP_COOKIE' in environ:
            logout = '<p><a href="/logout">Logout</a></p>'
            return['You are logged in'.encode() + logout.encode()]
        else:
            createaccount = '<p><a href="/">Create an account</a></p>'
            return ['You are logged in'.encode() + createaccount.encode()]


    elif path == '/':
        form = '''
        <!DOCTYPE html>
<html>
<head><title>Login Form</title></head>
<body>
<h1>Register or Login</h1>
<form action="/register">
    <h2>Register</h2>
    Create Username <input type="text" name="username"><br>
    Create Password <input type="password" name="password"><br>
    <input type="submit" value="Create account">
</form>

<form action="/login">
    <h2>Login</h2>
    Enter Username <input type="text" name="username"><br>
    Enter Password <input type="password" name="password"><br>
    <input type="submit" value="Login">
</form>'''

        start_response('200 OK', headers)
        return[form.encode()]

    else:
        start_response('404 Not Found', headers)
        return ['Status 404: Resource not found'.encode()]

httpd = wsgiref.simple_server.make_server('', 8000, application)
httpd.serve_forever()