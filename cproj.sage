import sys
import pdb


def n_equal(c1, c2, precision=None):
    if precision is None:
        precision = .9 * c1.prec()

    return (log(abs(c1 - c2)/abs(c1), 2).N() < -precision)


def get_cproj_data(root_system, n_of_v_0):
    R = RootSystem(root_system)
    W = WeylGroup(R)
    A = R.ambient_space()

    v_0 = A.fundamental_weight(n_of_v_0)
    weyl_orbit = v_0.orbit()
    len_orbit = len(weyl_orbit)

    w_coxeter = W.unit()

    for w_i in W.simple_reflections():
        w_coxeter = w_coxeter * w_i

    # Get the dual coxeter number and the dimension of the 
    # orthonormal basis of the root system
    root_system_type, root_system_rank = R.cartan_type()
    g = R.cartan_type().dual_coxeter_number()
    m_1 = 1                     # the smallest exponent
    xi = exp(2*pi*I*m_1/g)      # coxeter plane eigenvector 

    for eigendata in w_coxeter.matrix().change_ring(CDF).eigenvectors_right():
        val, vec, deg = eigendata
        if len(vec) > 1:
            sys.stderr.write("More than one eigenvector found.")
        if n_equal(val, xi) is True:
            v_c = vec[0]

    # Get the values of the superpotential at critical points.
    W_critical = []
    for v_i in weyl_orbit:
        W_i = 0
        for j in range(A.dimension()):
            W_i += v_i[j]*v_c[j]
        W_critical.append(complex(W_i))

    # Build a table to record solitons from simple Weyl reflections.
    simple_soliton_table = [
        [None for i in range(len_orbit)] for i in range(len_orbit)
    ]

    for i in range(len_orbit):
        v_i = weyl_orbit[i]
        for k, alpha_k in enumerate(A.roots()):
            w_v_i = v_i.reflection(alpha_k)
            for j in range(len_orbit):
                if j == i:
                    continue
                v_j = weyl_orbit[j]
                if v_j == w_v_i:
                    n = ((v_j - v_i).inner_product(alpha_k)/
                         (alpha_k.inner_product(alpha_k)))
                    simple_soliton_table[i][j] = (k, n)
                
    data = {
        "weyl_orbit_strs": [str(v) for v in weyl_orbit],
        "W_critical": W_critical,
        "root_strs": [str(r) for r in A.roots()],
        "simple_soliton_table": simple_soliton_table,
        "coxeter_vector": tuple([complex(v_c_i) for v_c_i in v_c]),
    }

    return data

root_system = sys.argv[1]
n_of_v_0 = int(sys.argv[2])

print get_cproj_data(root_system, n_of_v_0)
