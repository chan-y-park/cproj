#!/usr/bin/env python

import sys, getopt
import subprocess

import matplotlib.pyplot as pyplot
import mpld3
import mpldatacursor

import pdb

root_system = sys.argv[1]
n_of_v_0 = sys.argv[2]

shortopts = "i:`"
longopts = [
    "use-mpld3",
]

optlist, args = getopt.getopt(sys.argv[3:], shortopts, longopts)

# Default values of options
weight_index = None
use_mpld3 = False
for opt, arg in optlist:
    if(opt == '-i'):
        weight_index = int(arg)
    elif(opt == "--use-mpld3"):
        use_mpld3 = True

#root_system = 'A3
#n_of_v_0 = 2

#root_system = input("Enter the root system (e.g. 'A3', 'D4'): ")

#n_of_v_0 = input("Enter the index of the fundamental weight "
#                 "(n of \\omega_n): ")

data_str = subprocess.check_output(
    ["sage", "cproj.sage", str(root_system), str(n_of_v_0)] 
)

# Unpack data from the sage script.
data = eval(data_str)
weyl_orbit = data["weyl_orbit"]
W_critical = data["W_critical"]
roots = data["roots"]
simple_soliton_table = data["simple_soliton_table"]

len_orbit = len(weyl_orbit)

title = root_system + "_" + str(n_of_v_0)

# Save the soliton table as a text file.
with open("./results/" + title + ".txt", 'w') as f:
    # List of weights 
    for i, v_i in enumerate(weyl_orbit):
        f.write("v_{} = {}\n".format(i, v_i))
    f.write('\n')
    # List of the values of W at critical points
    for i, W_i in enumerate(W_critical):
        f.write("W(v_{}) = {}\n".format(i, W_i))
    f.write('\n')
    # List of roots
    for k, alpha_k in enumerate(roots):
        f.write("alpha_{} = {}\n".format(k, alpha_k))
    f.write('\n')
    # Soliton table
    width = 10
    f.write("".ljust(width, ' '))
    for i in range(len_orbit):
        f.write("v_{}".format(i).rjust(width, ' '))
    f.write('\n')
    for i in range(len_orbit):
        f.write("v_{}".format(i).ljust(width, ' '))
        for j in range(len_orbit):
            f.write(str(simple_soliton_table[i][j]).rjust(width, ' '))
        f.write('\n')

# Plot a figure of the projection of the soliton polytope.
figure = pyplot.figure(title, facecolor='w')
pyplot.title(title)
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

# Plot critical points.
W_point_labels = ["v_{} = {}".format(i, v_i) 
                  for i, v_i in enumerate(weyl_orbit)]
W_points = pyplot.plot(
    [W_i.real for W_i in W_critical], 
    [W_i.imag for W_i in W_critical],
    'o',
    markersize=10,
    color='k',
    label=W_point_labels,
)
W_points = []
for i in range(len_orbit):
    W_i = W_critical[i]
    mplobjs = pyplot.plot(
        W_i.real, 
        W_i.imag,
        'o',
        markersize=10,
        color='k',
        label=W_point_labels[i],
    )
    W_points.append(mplobjs[0])


# Plot solitons connecting critical points.
soliton_labels = []
soliton_lines = []

if weight_index is None:
    i_list = range(len_orbit)
else:
    i_list = [weight_index]

for i in i_list:
    W_i = W_critical[i]
    for j in range(len_orbit):
        soliton_data = simple_soliton_table[i][j]
        if soliton_data is None:
            continue
        else:
            soliton, sign = soliton_data
        W_j = W_critical[j]
        label = "alpha_{} = {}".format(soliton, roots[soliton])
        mplobjs = pyplot.plot(
            [W_i.real, W_j.real], [W_i.imag, W_j.imag], '-',
            label=label,
        )
        soliton_lines.append(mplobjs[0])
        soliton_labels.append(label)

if use_mpld3 is True:
    for i, point in enumerate(W_points):
        W_point_tooltip = mpld3.plugins.PointLabelTooltip(
            point, [W_point_labels[i]],
        )
        mpld3.plugins.connect(figure, W_point_tooltip)

    for i, soliton in enumerate(soliton_lines):
        soliton_tooltip = mpld3.plugins.LineLabelTooltip(
            soliton, [soliton_labels[i]],
        )
        mpld3.plugins.connect(figure, soliton_tooltip)

    mpld3.show()
else:
    mpldatacursor.datacursor(
        formatter="{label}".format,
        display="multiple",
        draggable=True,
    )
    pyplot.show()
