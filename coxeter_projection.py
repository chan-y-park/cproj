#!/usr/bin/env python

import subprocess
import random
from cStringIO import StringIO


import pdb


class CoxeterProjection:
    def __init__(
        self, root_system=None, n_of_v_0=None, is_interactive=True,
        message_queue=None, result_queue=None,
    ):
        self.root_system = root_system
        self.n_of_v_0 = n_of_v_0
        self.is_interactive = is_interactive
        self.message_queue = message_queue
        self.result_queue = result_queue
        self.weyl_orbit = None
        self.W_critical = None
        self.roots = None
        self.simple_soliton_table = None
        self.v_c = None


    def get_sage_data(self):
        self.message("Starting a SAGE script...")
        data_str = subprocess.check_output(
            ["sage", "cproj.sage", str(self.root_system), str(self.n_of_v_0)] 
        )
        self.message("Finished running the SAGE script.")

        # Unpack data from the sage script.
        data = eval(data_str)
        self.weyl_orbit = data["weyl_orbit"]
        self.W_critical = data["W_critical"]
        self.roots = data["roots"]
        self.simple_soliton_table = data["simple_soliton_table"]
        self.v_c = data["coxeter_vector"]


    def message(self, msg):
        if self.is_interactive is True:
            print msg
        else:
            self.message_queue.put(msg)


    def plot(self, weight_index=None):
        #XXX: Is there a way to put these imports in the beginning of a 
        #     module?
        import matplotlib
        #matplotlib.rcParams["savefig.directory"] = "./"
        if self.is_interactive is True:
            matplotlib.use('TkAgg')
        else:
            matplotlib.use('Agg')
        import mpldatacursor
        import matplotlib.pyplot as pyplot

        title = self.root_system + "_" + str(self.n_of_v_0)

        # Plot a figure of the projection of the soliton polytope.
        figure = pyplot.figure(title, facecolor='w', figsize=(6, 6), dpi=200,)
        pyplot.axis('off')
        #pyplot.tick_params(
        #    axis="both",
        #    which="both",
        #    bottom="off",
        #    top="off",
        #    left="off",
        #    right="off",
        #    labelbottom="off",
        #    labelleft="off",
        #)
        pyplot.axes().set_aspect('equal')

        mpldatacursor_artists = []
        # Plot critical points.
        W_point_labels = ["$v_{{{}}} = {}$".format(i, v_i) 
                          for i, v_i in enumerate(self.weyl_orbit)]
        W_points = []
        for i in range(len(self.weyl_orbit)):
            W_i = self.W_critical[i]
            mplobjs = pyplot.plot(
                W_i.real, 
                W_i.imag,
                'o',
                markersize=20,
                markeredgewidth=1.5,
                markerfacecolor='w',
                color='k',
                label=W_point_labels[i],
            )[0]
            pyplot.text(
                W_i.real, W_i.imag, str(i),
                fontsize=15,
                verticalalignment='center',
                horizontalalignment='center',
            )
            mpldatacursor_artists.append(mplobjs)


        # Plot solitons connecting critical points.
        soliton_colormap = matplotlib.cm.ScalarMappable(
            norm=matplotlib.colors.Normalize(vmin=0, vmax=len(self.roots)),
            cmap=matplotlib.cm.get_cmap('jet'), 
        )
        soliton_colors = [soliton_colormap.to_rgba(i)
                          for i in range(len(self.roots))]
        random.shuffle(soliton_colors)
        #colors = ['b', 'r', 'g', 'c', 'm', 'y']
        #soliton_colors = [colors[i%6] for i in range(len(roots))]


        if weight_index is None:
            i_list = range(len(self.weyl_orbit))
        else:
            i_list = [weight_index]

        for i in i_list:
            W_i = self.W_critical[i]
            for j in range(len(self.weyl_orbit)):
                #if j <= i:
                #    continue
                soliton_data = self.simple_soliton_table[i][j]
                if soliton_data is None:
                    continue
                else:
                    soliton, sign = soliton_data
                W_j = self.W_critical[j]
                if sign == -1:
                    sign_str = '-'
                else:
                    sign_str = ''
                root = tuple([sign*r_k for r_k in self.roots[soliton]])
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

        # Adjust margins.
        margin = .1     # in percent
        pyplot.xlim(*[(1 + margin)*l for l in pyplot.xlim()])
        pyplot.ylim(*[(1 + margin)*l for l in pyplot.ylim()])


        if self.is_interactive is True:
            # Display the plot.
            pyplot.show()
        else:
            # Return PNG to web frontend.
            img = StringIO()
            pyplot.savefig(img)
            img.seek(0)
            return img

    def save(self, file_name): 
        # Save the soliton table as a text file.
        with open("./results/" + file_name + ".txt", 'w') as f:
            # List of weights 
            for i, v_i in enumerate(self.weyl_orbit):
                f.write("v_{} = {}\n".format(i, v_i))
            f.write('\n')
            # Coxeter vector 
            f.write("v_c = {}\n".format(self.v_c))
            f.write('\n')
            # List of the values of W at critical points
            for i, W_i in enumerate(self.W_critical):
                f.write("W(v_{}) = {}\n".format(i, W_i))
            f.write('\n')
            # List of roots
            for k, alpha_k in enumerate(self.roots):
                f.write("alpha_{} = {}\n".format(k, alpha_k))
            f.write('\n')
            # Soliton table
            width = 10
            f.write("".ljust(width, ' '))
            for i in range(len(self.weyl_orbit)):
                f.write("v_{}".format(i).rjust(width, ' '))
            f.write('\n')
            for i in range(len(self.weyl_orbit)):
                f.write("v_{}".format(i).ljust(width, ' '))
                for j in range(len(self.weyl_orbit)):
                    f.write(str(self.simple_soliton_table[i][j])
                            .rjust(width, ' '))
                f.write('\n')