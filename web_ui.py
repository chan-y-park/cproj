import flask
import multiprocessing 
import time
import pdb
import cproj

# configuration
DEBUG = True
SECRET_KEY = 'coxeter projection key'

app = flask.Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def show_welcome():
    return flask.redirect(flask.url_for('get_config'))

@app.route('/config', methods=['GET', 'POST'])
def get_config():
    is_submitted = False
    config_items = {}
    if flask.request.method == 'GET' and bool(flask.request.args):
        set_config_items(config_items, flask.request.args)
    elif flask.request.method == 'POST':
        set_config_items(config_items, flask.request.form)

    if bool(config_items):
        if config_items['type'] == 'E':
            rank = int(config_items['rank'])
            if (rank != 6 and rank != 7 and rank != 8):
                flask.flash('The rank of an E-type should be 6, 7, or 8.')
                return flask.redirect(flask.url_for('get_config'))
            elif int(config_items['n_of_v_0']) != 1:
                flask.flash(
                    'Only 1 is allowed for the index of the fundamental '
                    'weight for {}.'.format(config_items['root_system'])
                )
                return flask.redirect(flask.url_for('get_config'))
        cproj.set_sage_data(
            root_system=config_items['root_system'],
            n_of_v_0_str=config_items['n_of_v_0']
        )
        return flask.redirect(
            flask.url_for(
                'show_result',
                root_system=config_items['root_system'],
                n_of_v_0=config_items['n_of_v_0'],
                weight_index=config_items['weight_index'],
            )
        )
        
    return flask.render_template('config.html')


@app.route('/result')
def show_result():
    root_system = flask.request.args.get('root_system')
    n_of_v_0_str = flask.request.args.get('n_of_v_0')
    n_of_v_0 = int(n_of_v_0_str)
    weight_index_str = flask.request.args.get('weight_index')
    try:
        weight_index = int(weight_index_str)
    except ValueError:
        weight_index = None
    
    sage_data_str = cproj.get_sage_data_str(root_system, n_of_v_0_str)
    data = eval(sage_data_str)
    weyl_orbit = data["weyl_orbit"]
    W_critical = data["W_critical"]
    roots = data["roots"]
    simple_soliton_table = data["simple_soliton_table"]
    v_c = data["coxeter_vector"]

    len_orbit = len(weyl_orbit)
    # Prepare v_c data
    v_c_str = '(' + ', '.join(
        '{:.3f}{:+.3f}i'.format(v_c_i.real, v_c_i.imag) for v_c_i in v_c
    ) + ')'
    # Prepare W_c data.
    W_c_str = ['{:.3f}{:+.3f}i'.format(W_c.real, W_c.imag)
        for W_c in W_critical
    ]
    # Prepare soliton data.
    solitons_str = [
        [None for i in range(len_orbit)] for i in range(len_orbit)
    ]
    for i, row in enumerate(simple_soliton_table):
        for j, entry in enumerate(row):
            if entry == None:
                solitons_str[i][j] = ''
                continue

            k, sign = entry
            if sign == -1:
                sign_str = '-'
            else:
                sign_str = ''
            solitons_str[i][j] = '{}\\alpha_{{ {} }}'.format(sign_str, k+1)

    return flask.render_template(
        'result.html', 
        root_system=root_system,
        n_of_v_0=n_of_v_0,
        weight_index=weight_index,
        weyl_orbit=weyl_orbit,
        W_c_str=W_c_str,
        roots=roots,
        solitons_str=solitons_str,
        v_c_str=v_c_str,
        len_orbit=len_orbit,
    )


@app.route('/plot')
def coxeter_projection_plot():
    root_system = flask.request.args.get('root_system')
    n_of_v_0_str = flask.request.args.get('n_of_v_0')
    n_of_v_0 = int(n_of_v_0_str)
    weight_index_str = flask.request.args.get('weight_index')
    try:
        weight_index = int(weight_index_str)
    except:
        weight_index = None

    img = cproj.plot_coxeter_projection(
        cproj.get_sage_data_str(root_system, n_of_v_0_str),
        root_system=root_system, 
        n_of_v_0=n_of_v_0,
        weight_index=weight_index,                   
        is_interactive=False,
    )
    rv = flask.send_file(img, mimetype='image/png', cache_timeout=0)
    rv.set_etag(str(time.time()))
    return rv


def set_config_items(config_items, request_dict):
    for key, value in request_dict.items():
        config_items[key] = value
    config_items['root_system'] = (
        request_dict['type'] + request_dict['rank']
    )

if __name__ == '__main__':
    app.run()
