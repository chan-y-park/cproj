import flask
import cproj
import multiprocessing
import pdb

# configuration
DEBUG = True
SECRET_KEY = 'coxeter projection key'

app = flask.Flask(__name__)
app.config.from_object(__name__)

logging_stream = cproj.set_logging('info')
result = multiprocessing.Queue()
main_process = None

@app.route('/')
def show_welcome():
    #return flask.render_template('index.html')
    return flask.redirect(flask.url_for('get_config'))

@app.route('/config', methods=['GET', 'POST'])
def get_config():
    if flask.request.method == 'POST':
        flask.session['root_system'] = flask.request.form['root_system']
        flask.session['n_of_v_0'] = flask.request.form['n_of_v_0']
        flask.session['progress'] = ''
        global main_process
        main_process = multiprocessing.Process(
            target=cproj.main, 
            kwargs={
                'root_system': flask.session['root_system'],
                'n_of_v_0': flask.session['n_of_v_0'],
                'use_mpld3': True,
                'result_queue': result,
            }
        )
        main_process.start()
        #return flask.redirect(flask.url_for('show_progress'))
        return flask.redirect(flask.url_for('show_result'))
    return flask.render_template('config.html')

@app.route('/progress', methods=['POST'])
def show_progress():
    if result.empty() is True:
        flask.session['progress'] += flask.session['logging_stream'].getvalue()
        return flask.Response(flask.session['progress'], mimetype="text/html") 
    else:
        flask.session['main_process'].join()
        return flask.redirect(flask.url_for('show_result'),
                              contents=[result.get()]) 

@app.route('/result')
def show_result():
    global main_process
    main_process.join()
    return flask.render_template('result.html', contents=[result.get()])

if __name__ == '__main__':
    app.run()
