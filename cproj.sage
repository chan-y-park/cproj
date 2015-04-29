import sys
import pdb


def n_equal(c1, c2, precision=None):
    if precision is None:
        precision = .9 * c1.prec()

    return (log(abs(c1 - c2)/abs(c1), 2).N() < -precision)

root_system = sys.argv[1]
n_of_v_0 = int(sys.argv[2])

R = RootSystem(root_system)
W = WeylGroup(R)
L = R.weight_space()
A = R.ambient_space()

v_0 = A.fundamental_weight(n_of_v_0)
weyl_orbit = v_0.orbit()
len_orbit = len(weyl_orbit)

w_coxeter = W.unit()

for w_i in W.simple_reflections():
    w_coxeter = w_coxeter * w_i

#print "{}\n".format(w_coxeter)

root_system_type = root_system[0]
root_system_rank = int(root_system[1:])
# Get the dual coxeter number and the dimension of the 
# orthonormal basis of the root system
if root_system_type is 'A':
    
    g = root_system_rank + 1
elif root_system_type is 'D':
    g = 2*root_system_rank -2
m_1 = 1                     # the smallest exponent
xi = exp(2*pi*I*m_1/g)      # coxeter plane eigenvector 

#print "Coxeter plane eigenvalue: {}".format(xi)

for eigendata in w_coxeter.matrix().change_ring(CDF).eigenvectors_right():
    val, vec, deg = eigendata
    #print "{0.real:.5f}+{0.imag:.5f}I, {1}, {2}".format(complex(val), vec, deg)
    if len(vec) > 1:
        sys.stderr.write("More than one eigenvector found.")
    #if log(abs(val - xi)/abs(xi), 2).N() < -(.9 * val.prec()):
    if n_equal(val, xi) is True:
        #print "Found coxeter plane eigenvector:"
        #print "\teigenvalue = {}".format(val)
        #print "\teigenvector = {}".format(vec[0])
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
    "weyl_orbit": weyl_orbit,
    "W_critical": W_critical,
    "roots": A.roots(),
    "simple_soliton_table": simple_soliton_table,
}

print data
