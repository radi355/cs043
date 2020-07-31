import wsgiref.simple_server
import urllib.parse
import sqlite3
import http.cookies
import random

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
            returnregister = '<p><a href="/account">Play multiplication game</a></p>'
            return ['User {} was successfully registered'.format(un).encode() + returnregister.encode()]


    elif path == '/login' and un and pw:
        user = cursor.execute('SELECT * FROM info WHERE username = ? AND password = ?', [un, pw]).fetchall()
        if user:
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            start_response('200 OK', headers)
            returnlogin = '<p><a href="/account">Play multiplication game</a></p>'
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

        if 'HTTP_COOKIE' not in environ:
            return ['Not logged in <a href="/">Login</a>'.encode()]

        cookies = http.cookies.SimpleCookie()
        cookies.load(environ['HTTP_COOKIE'])

        if 'session' not in cookies:
            return ['Not logged in <a href="/">Login</a>'.encode()]

        [un, pw] = cookies['session'].value.split(':')
        user = cursor.execute('SELECT * FROM info WHERE username = ? AND password = ?', [un, pw]).fetchall()

        # This is where the game begins. This section of is code only executed if the login form works, and if the user is successfully logged in

        if user:
            if 'score' not in cookies:
                correct = 0
                wrong = 0
            else:
                correct = int(cookies['score'].value.split(':')[0])
                wrong = int(cookies['score'].value.split(':')[1])
                cookies.load('score={}:{}'.format(correct, wrong))

            page = '<!DOCTYPE html><html><head><title>Multiply with Score</title></head><body>'

            if 'factor1' in params and 'factor2' in params and 'answer' in params:
                if int(params['answer'][0]) == int(params['factor1'][0]) * int(params['factor2'][0]):
                    page += '<p style="background-color: lightgreen">Correct, {} x {} = {}</p>'.format(int(params['factor1'][0]), int(params['factor2'][0]), int(params['factor1'][0]) * int(params['factor2'][0]))
                    correct += 1
                else:
                    page += '<p style="background-color: red">Wrong, {} x {} = {}, not {}</p>'.format(int(params['factor1'][0]), int(params['factor2'][0]), int(params['factor1'][0]) * int(params['factor2'][0]), int(params['answer'][0]))
                    wrong += 1

            elif 'reset' in params:
                correct = 0
                wrong = 0

            headers.append(('Set-Cookie', 'score={}:{}'.format(correct, wrong)))

            f1 = random.randrange(1, 11)
            f2 = random.randrange(1, 11)
            page += '<h1>What is {} x {}</h1>'.format(f1, f2)
            correctAnswer = f1 * f2
            answers = [correctAnswer, random.randrange(1, 101), random.randrange(1, 101), random.randrange(1, 101)]
            while answers[1] == correctAnswer or answers[2] == correctAnswer or answers[3] == correctAnswer:
                answers = [correctAnswer, random.randrange(1, 101), random.randrange(1, 101), random.randrange(1, 101)]
                random.shuffle(answers)
            random.shuffle(answers)

            page += '<a href="/account?username={}&amp;password={}&amp;factor1={}&amp;factor2={}&amp;answer={}">{}: {}</a><br>'.format(
                un, pw, f1, f2, answers[0], 'A', answers[0])
            page += '<a href="/account?username={}&amp;password={}&amp;factor1={}&amp;factor2={}&amp;answer={}">{}: {}</a><br>'.format(
                un, pw, f1, f2, answers[1], 'B', answers[1])
            page += '<a href="/account?username={}&amp;password={}&amp;factor1={}&amp;factor2={}&amp;answer={}">{}: {}</a><br>'.format(
                un, pw, f1, f2, answers[2], 'C', answers[2])
            page += '<a href="/account?username={}&amp;password={}&amp;factor1={}&amp;factor2={}&amp;answer={}">{}: {}</a><br>'.format(
                un, pw, f1, f2, answers[3], 'D', answers[3])

            page += '''
                    <h2>Score</h2>
                    Correct: {}<br>
                    Wrong: {}<br>
                    <a href="/account?reset=true">Reset</a>
                    </body></html>'''.format(correct, wrong)

            page += '<p><a href="/logout">Logout</a></p>'
            return [page.encode()]

        else:
            return ['Not logged in. <a href="/">Login</a>'.encode()]

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
        return [form.encode()]

    else:
        start_response('404 Not Found', headers)
        return ['Status 404: Resource not found'.encode()]


httpd = wsgiref.simple_server.make_server('', 8000, application)
httpd.serve_forever()