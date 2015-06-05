#!/usr/bin/env python

import os, sys, getopt
import subprocess
import random
from math import ceil, log10
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
    is_interactive=True,
):
    #XXX: Is there a way to put these imports in the beginning of a 
    #     module?
    import matplotlib
    if is_interactive is True:
        matplotlib.use('TkAgg')
    else:
        matplotlib.use('Agg')
    import mpldatacursor
    import matplotlib.pyplot as pyplot

    pyplot.clf()

    matplotlib.rcParams["savefig.directory"] = "./"

    # Unpack data from the sage script.
    data = eval(sage_data_str)
    weyl_orbit = data["weyl_orbit"]
    W_critical = data["W_critical"]
    roots = data["roots"]
    simple_soliton_table = data["simple_soliton_table"]
    v_c = data["coxeter_vector"]

    title = root_system + "_" + str(n_of_v_0)

    # Plot a figure of the projection of the soliton polytope.
    figure = pyplot.figure(
        title, facecolor='w', figsize=(8, 8), 
        #dpi=100,
    )
    pyplot.axis('off')

    pyplot.axes().set_aspect('equal')

    mpldatacursor_artists = []

    # Plot critical points.
    W_marker_size = 25
    W_font_size = 18.0/ceil(log10(len(weyl_orbit)))
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
            ','.join(str(i+1) for i in indices),
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
    #colors = ['b', 'r', 'g', 'c', 'm', 'y']
    #soliton_colors = [colors[i%6] for i in range(len(roots))]


    if (weight_index is None 
        or weight_index > len(weyl_orbit) 
        or weight_index < 1):
        i_list = range(len(weyl_orbit))
    else:
        i_list = [weight_index-1]

    for i in i_list:
        W_i = W_critical[i]
        for j in range(len(weyl_orbit)):
            #if j <= i:
            #    continue
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
            # Draw an arrow from v_i to v_j
#                mplobjs = pyplot.annotate(
#                    '',
#                    xy=(W_j.real, W_j.imag),
#                    xytext=(W_i.real, W_i.imag),
#                    arrowprops=dict(
#                        edgecolor=None,
#                        facecolor=soliton_colors[soliton], 
#                        shrink=.1,
#                    )
#                )
            offset = .075
            x = W_i.real
            y = W_i.imag
            dx = W_j.real - x
            dy = W_j.imag - y
            mplobjs = pyplot.arrow(
                x + (offset * dx), 
                y + (offset * dy), 
                (1 - 2*offset)*dx, 
                (1 - 2*offset)*dy, 
                length_includes_head=True,
                #shape='left',
                width=.002,
                head_width=.03,
                head_length=.045,
                label=label, color=soliton_colors[soliton],
            )
            # Draw a line from v_i to v_j
            #mplobjs = pyplot.plot(
            #    [W_i.real, W_j.real], [W_i.imag, W_j.imag], '-',
            #    label=label, color=soliton_colors[soliton],
            #)[0]
            mpldatacursor_artists.append(mplobjs)

    mpldatacursor.datacursor(
        artists=mpldatacursor_artists,
        formatter="{label}".format,
        display="multiple",
        draggable=True,
    )

    pyplot.margins(.05)

    if is_interactive is True:
        # Display the plot.
        pyplot.show()
    else:
        # Return PNG to web frontend.
        img = BytesIO()
        pyplot.savefig(img)
        img.seek(0)
        return img

#        if not os.path.exists(PLOT_DIR):
#            os.makedirs(PLOT_DIR)
#
#        plot_file_name = root_system + '_' + str(n_of_v_0)
#        if weight_index is not None:
#            plot_file_name += '_' + str(weight_index)
#        plot_file_name += '.png'
#        plot_file_path = PLOT_DIR + plot_file_name
#        if not os.path.isfile(plot_file_path):
#            pyplot.savefig(plot_file_path)
#        return plot_file_path

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
    #root_system = input("Enter the root system (e.g. 'A3', 'D4'): ")

    #n_of_v_0 = input("Enter the index of the fundamental weight "
    #                 "(n of \\omega_n): ")
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
