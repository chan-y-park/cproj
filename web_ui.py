import flask
import multiprocessing 
import pdb
import cproj
from coxeter_projection import CoxeterProjection, web_process

# configuration
DEBUG = True
SECRET_KEY = 'coxeter projection key'

app = flask.Flask(__name__)
app.config.from_object(__name__)

message_queue = multiprocessing.Queue()
input_queue = multiprocessing.Queue()
output_queue = multiprocessing.Queue()

cp_process = None

@app.route('/')
def show_welcome():
    #return flask.render_template('index.html')
    return flask.redirect(flask.url_for('get_config'))

@app.route('/config', methods=['GET', 'POST'])
def get_config():
    if flask.request.method == 'POST':
        flask.session['root_system'] = flask.request.form['root_system']
        flask.session['n_of_v_0'] = flask.request.form['n_of_v_0']
        global cp_process, message_queue, input_queue, output_queue
        cp_process = multiprocessing.Process(
            target=web_process, 
            kwargs={
                'root_system': flask.session['root_system'],
                'n_of_v_0': flask.session['n_of_v_0'],
                'message_queue': message_queue,
                'input_queue': input_queue,
                'output_queue': output_queue,
            }
        )
        cp_process.start()
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
        global message_queue
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
    global cp_process
    cp_process.join()
    return flask.render_template(
        'result.html', 
    )


@app.route('/plot')
def coxeter_projection_plot():
    global output_queue 
    cp = output_queue.get()
    img = cp.plot()
    return flask.send_file(img, mimetype='image/png')

if __name__ == '__main__':
    app.run()
