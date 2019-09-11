from flask import Flask

app = Flask(__name__)


@app.route('/send_mail')
def send_mail():
    import send_mail
    return send_mail.app()

@app.route('/user/signup')
def user_signup():
    import user_signup as user
    return user.signup()

@app.route('/user/confirm')
def user_confirm():
    import user_signup as user
    return user.confirm()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
