import numpy as np
import matplotlib.pyplot as plt

from scipy.integrate import odeint


def get_vi_prime(nc, m, x, i, j):
    """ contribution to the 2d acceleration of particle i, caused by particle j (in 2-body problem)
        Args:
            nc: charge numbers of all particles
            m: masses of all particles
            x: array of position vectors of all particles (N stacked 3-component np.array)
            i: index of affected particle; assumption: two dimensions, i.e. i and j are the only two particle indices needed to calculate the forces;
            j: index of particle which creates the contribution to the field (source particle)
        Returns:
            accelleration vector vi_prime (3-component np.array) """
    e = 1  # elementary charge
    # e = np.sqrt(0.5)

    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
    return ((e**2. * nc[i] * nc[j] * (np.array(x[i]) - np.array(x[j])) / np.linalg.norm(x[i] - x[j])**3.)  # coulomb force between two point particles
            / m[i])

def calc_first_derivatives(w, t, p):
    """ Args:
            w: state variables (i.e. the variables out of which a set of first order derivatives is computed) [v1, v2, x1, x2],
            t: time,
            p: parameters (all other parameters appearing in the equations, e.g. constants) """

    N = 2  # number of particles (kept constant for now, to two)
    d = 2  # dimensionality of the problem (kept constant for now, to two)

    # -- extract the symbols from the state variable vector
    # v1 and v2 (both have two components, i.e. two dimensional)
    w_partitioned = np.reshape(w, (-1, d))
    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
    v_partitioned = w_partitioned[0:N]
    x_partitioned = w_partitioned[N:2*N]
    assert len(v_partitioned) == len(x_partitioned)

    m = p[0:N]  # masses (two partilces, with m1 and m2)
    # charge numbers nc1 and nc2 (can be both positive or negative)
    nc = p[N:2*N]

    # -- write down the expressions for the first derivatives of the state varibles,
    #    in the same order as extraction of the state variables from the state variable vector

    v_prime = np.zeros((N, d))  # store vectors in there
    x_prime = v_partitioned

    # count all contributions, count them twice in fact! Then at the end, divide by two
    for i in range(N):
        for j in range(N):
            if not i == j:
                # append a 2d vector to a list -> later flatten the list
                v_prime[i] += get_vi_prime(nc, m, x_partitioned, i, j) / 2.

    return list(np.ravel([v_prime, x_prime]))


def get_pos_as_func_of_time(stoptime=10.0, numpoints=250, m1=1, m2=2, nc1=-1., nc2=1.,
                            v1=(0., 0.), v2=(0., 0.1), x1=(-0.5, 0.), x2=(+0.5, 0.)):
    """ Args:
        Returns:
            list of [t, x1_vec, x2_vec], where t contains times and x1_vec (or x2_vec) is a list of d-dimensional numpy arrays at that time """
    # solver parameters
    # TODO: play with these
    abserr = 1.0e-8
    relerr = 1.0e-6

    # time sample
    t = [stoptime * float(i) / (numpoints - 1) for i in range(numpoints)]

    # -- Pack up the parameters and initial conditions
    # ---- equal masses, repulsive
    p = [m1, m2, nc1, nc2]  # m1, m2, nc1, nc2
    # ---- initially at rest, at distance 1 from each other, on the x axis, centered around origin

    w0 = list(np.ravel([v1, v2, x1, x2])) # [v1, v2, x1, x2]
    # w0 = list(np.ravel([(1., 0.), (-1, 0.), (-0.5, 0.), (+0.5, 0.)])) # [v1, v2, x1, x2]

    # Call the ODE solver.
    wsol = odeint(calc_first_derivatives, w0, t, args=(p,),
                  atol=abserr, rtol=relerr)

    # wsol has an array of values for each value of t.
    # I want the columns of wsol

    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

    # print("hi")


    # # plot the positions as a function of time
    # plt.plot(t, wsol[:,4], label="x_1")
    # plt.plot(t, wsol[:,5], label="y_1")
    # plt.plot(t, wsol[:,6], label="x_2")
    # plt.plot(t, wsol[:,7], label="y_2")

    # plt.legend()

    # plt.show()

    return [t, np.transpose([wsol[:,4], wsol[:,5]]), np.transpose([wsol[:,6], wsol[:,7]]), np.transpose([wsol[:,0], wsol[:,1]]), np.transpose([wsol[:,2], wsol[:,3]])]
