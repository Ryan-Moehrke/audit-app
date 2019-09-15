from flask import Flask, g, request, render_template

app = Flask(__name__)
def homeButton(text):
    return "<p>{}</p><form action='/'><button type='submit'>Home</button>".format(text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_mail', methods=['POST'])
def send_mail():
    import send_mail
    person = request.form
    if not person["Email"]:
        return homeButton("An Email Address Is Required")
    elif not person["Given"] and not person["Family"]:
        return homeButton("A Patient Name Is Required To Search")
    else:
        text = send_mail.sendSingleMail(person, True)
        return homeButton(text)

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
