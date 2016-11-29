#!/usr/bin/env python
# Force integer division to give a float, i.e. 1/2 = 0.5.
from __future__ import division
import os, sys, getopt
import subprocess
import random
from math import ceil, log10, sqrt
from io import BytesIO
import pdb

DATA_DIR = './data/'
PLOT_DIR = './static/'


def set_sage_data(root_system=None, n_of_v_0_str=None,):
    data_file_path = DATA_DIR + root_system + '_' + n_of_v_0_str
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.isfile(data_file_path):
        sage_data_str = subprocess.check_output(
            ["sage", "cproj.sage", root_system, n_of_v_0_str] 
        )
        with open(data_file_path, 'w') as f:
            f.write(sage_data_str)


def get_sage_data_str(root_system=None, n_of_v_0_str=None,):
    data_file_path = DATA_DIR + root_system + '_' + n_of_v_0_str
    with open(data_file_path, 'r') as f:
        sage_data_str = f.read()
    return sage_data_str


def plot_coxeter_projection(
    sage_data_str, root_system=None, n_of_v_0=None, weight_index=None,
    is_interactive=True, image_format=None,
):
    import matplotlib
    if is_interactive:
        matplotlib.use('TkAgg')
    else:
        matplotlib.use('Agg')
    import mpldatacursor
    import matplotlib.pyplot as pyplot

    if not is_interactive:
        pyplot.clf()

    # Unpack data from the sage script.
    data = eval(sage_data_str)
    weyl_orbit_strs = data["weyl_orbit_strs"]
    W_critical = data["W_critical"]
    root_strs = data["root_strs"]
    simple_soliton_table = data["simple_soliton_table"]
    v_c = data["coxeter_vector"]

    weyl_orbit = [eval(v_str) for v_str in weyl_orbit_strs]
    roots = [eval(r_str) for r_str in root_strs]

    title = root_system + "_" + str(n_of_v_0)

    max_n_digits = ceil(log10(len(weyl_orbit)))

    # Plot a figure of the projection of the soliton polytope.
    figure_size = 6 * max_n_digits
    figure = pyplot.figure(
        title, facecolor='w',
        figsize=(figure_size, figure_size), 
    )
    pyplot.axis('off')

    pyplot.axes().set_aspect('equal')

    mpldatacursor_artists = []

    # Plot critical points.
    W_marker_size = 25
    W_font_size = 18.0 / max_n_digits
    W_point_labels = ["$v_{{{}}} = {}$".format(i, v_i) 
                      for i, v_i in enumerate(weyl_orbit)]

    grouped_W_c = group_degenerate_W_c(W_critical)
    for W, indices in grouped_W_c:
        mplobjs = pyplot.plot(
            W.real, W.imag,
            'o',
            markersize=W_marker_size,
            markeredgewidth=1.5,
            markerfacecolor='w',
            color='k',
            label=', '.join(W_point_labels[i] for i in indices),
        )
        pyplot.text(
            W.real, W.imag,
            ','.join(str(i + 1) for i in indices),
            fontsize=W_font_size/len(indices),
            verticalalignment='center',
            horizontalalignment='center',
        )

        if is_interactive:
            mpldatacursor_artists.append(mplobjs[0])

    # Plot solitons connecting critical points.
    soliton_colormap = matplotlib.cm.ScalarMappable(
        norm=matplotlib.colors.Normalize(vmin=0, vmax=len(roots)),
        cmap=matplotlib.cm.get_cmap('jet'), 
    )
    soliton_colors = [soliton_colormap.to_rgba(i)
                      for i in range(len(roots))]
    random.shuffle(soliton_colors)

    if (weight_index is None 
        or weight_index > len(weyl_orbit) 
        or weight_index < 1):
        i_list = range(len(weyl_orbit))
    else:
        i_list = [weight_index-1]

    for i in i_list:
        W_i = W_critical[i]
        for j in range(len(weyl_orbit)):
            soliton_data = simple_soliton_table[i][j]
            if soliton_data is None:
                continue
            else:
                soliton, sign = soliton_data
            W_j = W_critical[j]
            if sign == -1:
                sign_str = '-'
            else:
                sign_str = ''
            root = tuple([sign*r_k for r_k in roots[soliton]])
            label = "${}\\alpha_{{{}}} = {}$".format(
                sign_str, soliton, root
            )

            offset = .05 / max_n_digits
            x = W_i.real
            y = W_i.imag
            dx = W_j.real - x
            dy = W_j.imag - y
            r = sqrt(dx**2 + dy**2)
            mplobjs = pyplot.arrow(
                x + (offset * dx)/r, 
                y + (offset * dy)/r, 
                (1 - 2*offset/r)*dx, 
                (1 - 2*offset/r)*dy, 
                length_includes_head=True,
                label=label, color=soliton_colors[soliton],
            )

            mpldatacursor_artists.append(mplobjs)

    mpldatacursor.datacursor(
        artists=mpldatacursor_artists,
        formatter="{label}".format,
        display="multiple",
        draggable=True,
    )

    pyplot.margins(.05)

    if is_interactive is True:
        matplotlib.rcParams["savefig.directory"] = "./"
        # Display the plot.
        pyplot.show()
    else:
        # Return the plot to web frontend.
        img = BytesIO()
        pyplot.savefig(img, format=image_format)
        img.seek(0)
        return img


def group_degenerate_W_c(W_c):
    # grouped_W_c = [[W_i, [i_1, i_2, ...]], [W_j, [j_1, j_2, ...]], ...]
    grouped_W_c = []
    epsilon = 1e-6
    for i, W_i in enumerate(W_c):
        is_new = True
        for j, W_group in enumerate(grouped_W_c):
            W = W_group[0]
            if abs(W_i - W) < epsilon:
                W_group[1].append(i)
                is_new = False
                break
        if is_new:
            grouped_W_c.append([W_i, [i]])

    return grouped_W_c


if __name__ == '__main__':
    root_system = sys.argv[1]
    n_of_v_0 = sys.argv[2]

    shortopts = 'i:'
    longopts = ''
    optlist, args = getopt.getopt(sys.argv[3:], shortopts, longopts)

    weight_index = None

    for opt, arg in optlist:
        if(opt == '-i'):
            weight_index = int(arg)

    set_sage_data(root_system, n_of_v_0)
    sage_data_str = get_sage_data_str(root_system, n_of_v_0)
    plot_coxeter_projection(sage_data_str, root_system, n_of_v_0, weight_index)
