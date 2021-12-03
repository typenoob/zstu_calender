from flask import Flask, request, render_template, flash, send_file, send_from_directory
import os
import datetime
app = Flask(__name__)
app.secret_key = 'chen..02'


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name


@app.route('/login', methods=['POST'])
def login():
    xh = request.form['xh']
    mm = request.form['mm']
    directory = os.getcwd()
    return send_from_directory(directory, 'cqupt.ics', as_attachment=True)


if __name__ == '__main__':

    app.run(debug=True)
