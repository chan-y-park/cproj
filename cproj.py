#!/usr/bin/env python

import sys
import subprocess

import matplotlib.pyplot as pyplot
import mpld3

import pdb

root_system = sys.argv[1]
n_of_v_0 = sys.argv[2]

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
with open(title + ".txt", 'w') as f:
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
figure = pyplot.figure(title)
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
W_points = pyplot.plot(
    [W_i.real for W_i in W_critical], 
    [W_i.imag for W_i in W_critical],
    'o',
    color='k'
)
W_point_labels = [str(i) for i in range(len_orbit)]

W_point_tooltip = mpld3.plugins.PointLabelTooltip(
    W_points[0], W_point_labels,
)
mpld3.plugins.connect(figure, W_point_tooltip)

# Plot solitons connecting critical points.
for i in range(len_orbit):
    W_i = W_critical[i]
    for j in range(len_orbit):
        soliton = simple_soliton_table[i][j]
        if soliton is None:
            continue
        W_j = W_critical[j]
        pyplot.plot([W_i.real, W_j.real], [W_i.imag, W_j.imag], '-')
 
#pyplot.show()
mpld3.show()
