import flask
import multiprocessing 
import time
import pdb
import cproj
from coxeter_projection import CoxeterProjection, web_process

# configuration
DEBUG = True
SECRET_KEY = 'coxeter projection key'

app = flask.Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def show_welcome():
    #return flask.render_template('index.html')
    return flask.redirect(flask.url_for('get_config'))

@app.route('/config', methods=['GET', 'POST'])
def get_config():
    flask.session['root_system'] = None
    flask.session['n_of_v_0'] = None
    flask.session['weight_index'] = None
    if flask.request.method == 'GET' and bool(flask.request.args):
        set_config_items(flask.session, flask.request.args)
    elif flask.request.method == 'POST':
        set_config_items(flask.session, flask.request.form)
    if flask.session['root_system'] is not None:
        return flask.redirect(flask.url_for('show_result'))
    return flask.render_template('config.html')


@app.route('/result')
def show_result():
    return flask.render_template(
        'result.html', 
    )


@app.route('/plot')
def coxeter_projection_plot():
    cp = CoxeterProjection(
        root_system=flask.session['root_system'], 
        n_of_v_0=flask.session['n_of_v_0'],
        weight_index=flask.session['weight_index'],                   
        is_interactive=False,
    )
    cp.get_sage_data()
    img = cp.plot()
    rv = flask.send_file(img, mimetype='image/png', cache_timeout=0)
    rv.set_etag(str(time.time()))
    return rv


def set_config_items(config_items, request_dict):
    for key, value in request_dict.items():
        if key == 'weight_index' or key == 'n_of_v_0':
            try:
                config_items[key] = int(value)
            except ValueError:
                config_items[key] = None
        else:
            config_items[key] = value

if __name__ == '__main__':
    app.run()
