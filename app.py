from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/connect')
def connect():
    return render_template('whatsapp_check.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/progress')
def progress():
    return render_template('progress.html')

@app.route('/summary')
def summary():
    return render_template('summary.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/security')
def security():
    return render_template('security.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/help')
def help_center():
    return render_template('help.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
