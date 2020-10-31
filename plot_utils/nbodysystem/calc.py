import numpy as np
import matplotlib.pyplot as plt

from scipy.integrate import odeint


def get_vi_prime(nc, m, x, i, j):
    """ contribution to the acceleration of particle i, caused by particle j
        Args:
            nc: charge numbers of all particles
            m: masses of all particles
            x: array of position vectors of all particles (N stacked d-component np.array)
            i: index of affected particle; assumption: two dimensions, i.e. i and j are the only two particle indices needed to calculate the forces;
            j: index of particle which creates the contribution to the field (source particle)
        Returns:
            accelleration vector vi_prime (d-component np.array) """
    e = 1  # elementary charge
    # e = np.sqrt(0.5)

    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
    return ((e**2. * nc[i] * nc[j] * (np.array(x[i]) - np.array(x[j])) / np.linalg.norm(x[i] - x[j])**3.)  # coulomb force between two point particles
            / m[i])

def calc_first_derivatives(w, t, p, N, d):
    """
    Args:
        w: state variables (i.e. the variables out of which a set of first order derivatives is computed) [v1, v2, x1, x2],
        t: time,
        p: parameters (all other parameters appearing in the equations, e.g. constants)
        N: number of bodies
        d: dimensionality of the problem
    """

    # N = 2  # number of particles (kept constant for now, to two)
    # d = 2  # dimensionality of the problem (kept constant for now, to two)

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
                # append a d-dimensional vector to a list -> later flatten the list
                v_prime[i] += get_vi_prime(nc, m, x_partitioned, i, j) / 2.

    return list(np.ravel([v_prime, x_prime]))

def get_pos_as_func_of_time(ms, ncs,
                            vis, xis,
                            stoptime=10.0, numpoints=250,
                            d=3, num_of_bodies=3):
    """
    Args:
        ms: masses
        ncs: charge numbers
        vis: initial velocities
        xis: initial positions
        d: dimensionality
        N: number of bodies

    Returns:
        tuple of (t, vels, poss), where t contains times and vels/poss are lists of size num_of_bodies of d-dimensional numpy arrays at that time """
    # solver parameters
    # TODO: play with these
    abserr = 1.0e-8
    relerr = 1.0e-6

    # time sample
    t = [stoptime * float(i) / (numpoints - 1) for i in range(numpoints)]

    # -- Pack up the parameters and initial conditions
    # ---- masses, charges
    import itertools
    p = list(itertools.chain(*[ms, ncs]))  # flatten a python list
    w0 = list(np.ravel([vis, xis]))  # flattened list of all initial coordinates

    # Call the ODE solver.
    wsol = odeint(calc_first_derivatives, w0, t, args=(p, num_of_bodies, d,),
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

    # Format of the return list:
    # t,
    # list of columns of lists of 3-d numpy arrays representing positions of each particle
    # list of columns of lists of 3-d numpy arrays representing velocities of each particle

    # velocities occur first in the solution vector
    vels = []
    poss = []
    for n in range(num_of_bodies):
        vels.append(wsol[:, n*d : (n+1)*d])  # 3-d, i.e. take 3 elements
        idx_offset = num_of_bodies*d
        poss.append(wsol[:, idx_offset + n*d : idx_offset + (n+1)*d])

    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
    return (t, vels, poss)  # np.transpose([wsol[:,4], wsol[:,5]]), np.transpose([wsol[:,6], wsol[:,7]]), np.transpose([wsol[:,0], wsol[:,1]]), np.transpose([wsol[:,2], wsol[:,3]])]
