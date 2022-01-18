from flask import Flask, redirect, url_for, request, render_template, flash, send_from_directory
import os
import main
import json
app = Flask(__name__)
app.secret_key = '123'


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name


@app.route('/login', methods=['POST'])
def login():
    config = {}
    config['sno'] = request.form['xh']
    config['password'] = request.form['mm']
    config['date'] = request.form['dt']
    with open("config.json", "w") as f:
        json.dump(config, f)
    msg = main.main()
    directory = os.getcwd()
    if str(msg) == 'successful!':
        return send_from_directory(directory, 'cqupt.ics', as_attachment=True)
    else:
        flash(msg)
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
