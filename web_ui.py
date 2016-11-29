import flask
import multiprocessing 
import time
from io import BytesIO
import pdb
import cproj

# Flask configuration.
DEBUG = True
SECRET_KEY = 'coxeter projection key'
# CACHE_TYPE = 'null'

app = flask.Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def show_welcome():
    return flask.redirect(flask.url_for('get_config'))


@app.route('/config', methods=['GET', 'POST'])
def get_config():
    config_items = {}
    if flask.request.method == 'GET' and bool(flask.request.args):
        set_config_items(config_items, flask.request.args)
    elif flask.request.method == 'POST':
        set_config_items(config_items, flask.request.form)

    if bool(config_items):
        # Form validity checks.
        try:
            rank = int(config_items['rank'])
        except ValueError:
            flask.flash('The rank should be a positive integer.')
            return flask.redirect(flask.url_for('get_config'))
        if rank < 0:
            flask.flash('The rank should be a positive integer.')
            return flask.redirect(flask.url_for('get_config'))

        try:
            n_of_v_0 = int(config_items['n_of_v_0'])
        except ValueError:
            flask.flash('Invalid fundamental weight index.')
            return flask.redirect(flask.url_for('get_config'))
        if n_of_v_0 < 1 or n_of_v_0 > rank:
            flask.flash('The fundamental weight index should be an integer'
                        ' between 1 and the rank.')
            return flask.redirect(flask.url_for('get_config'))

        if config_items['weight_index'] != '':
            try:
                weight_index = int(config_items['weight_index'])
            except ValueError:
                flask.flash('Invalid ground state index.')
                return flask.redirect(flask.url_for('get_config'))

        if config_items['type'] == 'E':
            if not (
                (rank == 6 and (n_of_v_0 == 1 or n_of_v_0 == 6)) or
                (rank == 7 and n_of_v_0 == 7)
            ):
                flask.flash('Incorrect data for E-type.')
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
    try:
        reconfig = eval(flask.request.form['reconfig'])
    except KeyError:
        reconfig = False
    if reconfig is True:
        return flask.redirect(
            flask.url_for(
                'get_config',
                type=flask.request.form['type'],
                rank=flask.request.form['rank'],
                n_of_v_0=flask.request.form['n_of_v_0'],
                weight_index=flask.request.form['weight_index'],
            )
        )
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
    weyl_orbit_strs = data["weyl_orbit_strs"]
    W_critical = data["W_critical"]
    root_strs = data["root_strs"]
    simple_soliton_table = data["simple_soliton_table"]
    v_c = data["coxeter_vector"]

    len_orbit = len(weyl_orbit_strs)
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
        type_str=root_system[0],
        rank_str=root_system[1:],
        weight_index_str=weight_index_str,
        root_system=root_system,
        n_of_v_0=n_of_v_0,
        weight_index=weight_index,
        weyl_orbit_strs=weyl_orbit_strs,
        W_c_str=W_c_str,
        root_strs=root_strs,
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

    attachment_filename = root_system + '_' + n_of_v_0_str
    if weight_index_str is not None:
        attachment_filename += '_' + weight_index_str

    image_format = flask.request.args.get('image_format', None)
    if image_format == 'svg':
        image_mimetype = 'image/svg+xml'
        as_attachment = False 
        attachment_filename += '.svg'
    elif image_format == 'pdf':
        image_mimetype = 'application/pdf'
        as_attachment = False
        attachment_filename += '.pdf'
    else:
        image_mimetype = 'image/png'
        as_attachment = False 
        attachment_filename += '.png'

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
        image_format=image_format,
    )
    rv = flask.send_file(img, mimetype=image_mimetype, cache_timeout=0,
                         as_attachment=as_attachment,
                         attachment_filename=attachment_filename)
    rv.set_etag(str(time.time()))
    return rv


def set_config_items(config_items, request_dict):
    for key, value in request_dict.items():
        config_items[key] = value
    config_items['root_system'] = (
        request_dict['type'] + request_dict['rank']
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=True,)
