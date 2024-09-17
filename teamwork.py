## import libraries
from flask import render_template

from app import create_app

import webbrowser


# from flask import login_required

app = create_app()

# Global variable to keep track of whether the browser was opened
browser_opened = False

# @app.route('/secret')
# @login_required
# def secret():
#     return '只有认证用户可以访问'


@app.route('/')
def welcome():
    return render_template('welcome.html')  # Render the welcome page


@app.route('/user/login')
def login():
    return render_template('login.html')  # Ensure you have this template


if __name__ == '__main__':
    webbrowser.open_new('http://127.0.0.1:5000/')
    app.run(debug=False,host='127.0.0.1', port=5000)
    # app.run(host='0.0.0.0', port=5001)

