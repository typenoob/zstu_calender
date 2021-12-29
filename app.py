from flask import Flask, redirect, url_for, request, render_template, flash, send_from_directory
import os
import main
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
    rq = request.form['dt']
    os.system('sed -i \'1s/=.*/={xh}/\' login.js'.format(xh=xh))
    os.system('sed -i \'2s/=.*/="{mm}"/\' login.js'.format(mm=mm))
    if rq:
        msg = main.main(*map(int, rq.split('-')))
    else:
        msg = main.main()
    directory = os.getcwd()
    if str(msg) == 'successful!\n':
        return send_from_directory(directory, 'cqupt.ics', as_attachment=True)
    else:
        flash(msg)
        return redirect(url_for('hello'))


if __name__ == '__main__':
    app.run(debug=True)
