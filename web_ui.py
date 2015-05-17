import flask
import threading 
import Queue
import pdb
import cproj

# configuration
DEBUG = True
SECRET_KEY = 'coxeter projection key'

app = flask.Flask(__name__)
app.config.from_object(__name__)

message_queue = Queue.Queue()
result_queue = Queue.Queue()
main_thread = None
progress = None 

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
        global main_thread, progress
        progress = ''
        main_thread = threading.Thread(
            target=cproj.main, 
            kwargs={
                'root_system': flask.session['root_system'],
                'n_of_v_0': flask.session['n_of_v_0'],
                'use_mpld3': True,
                'message_queue': message_queue,
                'result_queue': result_queue,
            }
        )
        main_thread.start()
        return flask.redirect(flask.url_for('show_progress'))
    return flask.render_template('config.html')


def progress_stream_template(template_name, **context):
    # http://flask.pocoo.org/docs/patterns/streaming/#streaming-from-templates
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    return rv


@app.route('/progress', methods=['GET', 'POST'])
def show_progress():
    def yield_messages():
        global message_queue, progress
        message = message_queue.get()
        while (message != 'SUCCESS'):
            yield '<br>{}</br>\n'.format(message)
            message = message_queue.get()
        yield '<a href="result">Show result</a>\n' 
    return flask.Response(
        progress_stream_template('progress.html', progress=yield_messages())
    )

@app.route('/result')
def show_result():
    global main_thread, result_queue
    main_thread.join()
    return flask.render_template('result.html', contents=[result_queue.get()])

if __name__ == '__main__':
    app.run()
