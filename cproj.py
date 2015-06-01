#!/usr/bin/env python

import sys, getopt
import pdb
from coxeter_projection import CoxeterProjection

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

    cp = CoxeterProjection(root_system, n_of_v_0)
    cp.plot(weight_index)
