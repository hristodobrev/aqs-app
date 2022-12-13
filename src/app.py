from flask import Flask, url_for, abort, session, redirect, request
from markupsafe import escape

app = Flask(__name__)

# import secrets
# secrets.token_hex()
app.secret_key = b'nh:423RF098h#!#_0EIR_)RIFA"$#'

@app.route('/')
def index():
    if 'username' in session:
        username = session.get('username')
        return f'Home Page <br> Hello, {username}<br><a href="/logout">Logout</a>'
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))

    return '''
        <form method="POST">
            <p><input type="text" name="username" placeholder="Username"/></p>
            <p><input type="submit" value="Login"/></p>
        </form>
    '''

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return 'This is a simple Python app using Flask'

@app.route('/greeting/<name>')
def greeting(name):
    return f'Hello, {name}'

@app.route('/projects/')
def projects():
    return 'Projects page'

@app.route('/confidential/')
def confidential():
    abort(401)
    return 'Some sensitive data. Added some change!'

@app.route('/data')
def get_data():
    return [1,2,3,4]

@app.errorhandler(401)
def access_denied(error):
    return 'Access is denied!', 401
    
@app.errorhandler(404)
def not_found(error):
    return 'Page does not exist!', 404

with app.test_request_context():
    print(url_for('index'))
    print(url_for('about'))
    print(url_for('about', test='Something'))
    print(url_for('greeting', name='Pesho'))
    print(url_for('projects'))