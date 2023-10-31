import numpy as np
import scipy as sp

def attenuation(x, a, b):
    return b*np.exp(-a*x)


def attn_fit(args):
    dist_array = np.array([])
    min_array = np.array([])
    for i in args:
        dist_array = np.append(dist_array, i.dist_no_outliers)
        newmin = i.min_no_outliers/np.sqrt(i.dist_no_outliers)
        min_array = np.append(min_array, newmin)
    return sp.optimize.curve_fit(
        f=attenuation,
        xdata=dist_array,
        ydata=min_array,
        p0=np.array([0.02, 2.1e2])
    )


def inv1(x, a, b, c, d, f):
    return a*(1-np.exp(-b*x)) + c*(1-np.exp(-d*x)) + f*x


def inv1_fit(args): # returns fit of data to exponential function inv1
    dist_array = np.array([])
    tmin_array = np.array([])
    for i in args:
        dist_array = np.append(dist_array, i.dist)
        tmin_array = np.append(tmin_array, i.tmin)
    return sp.optimize.curve_fit(
        f=inv1,
        xdata=dist_array,
        ydata=tmin_array,
        # p0=np.array([0.85/100,0.035,1/1000,1.4, 1/3900]),
        p0=([0.011,0.04, 0.35, 0.005, 1/3800]),
        maxfev=10000000
    )


def inv1_slope(x, params):  # This will accept a tuple of parameters
    # returns slowness u=1/dtdx based on the derivative of the exponential distance-time function inv1
    a, b, c, d, f = params
    dtdx = a*b*np.exp(-b*x) + c*d*np.exp(-d*x) + f
    return 1/dtdx


def inv1_depth(dist, params):
    vel_grad = inv1_slope(dist, params)
    # vel_apparent = primary.dist_no_outliers/primary.tmin_no_outliers
    vel_apparent = dist/inv1(dist, *params)
    z = np.array([])
    for i in range(len(dist)):
        z_int = sp.integrate.quad(lambda x: 1/(np.arccosh(vel_grad[i]/vel_apparent[i])), 0, dist[i])
        z_temp = 1/np.pi * z_int[0]
        z = np.append(z, z_temp)
    return z, vel_grad


def inc_angle(primary, params):
    vmin = inv1_slope(primary.dist, params)
    vmax = inv1_slope(0, params)
    return np.arcsin(vmax/vmin)


def primary_amp(primary, attn_coeff, inc_angle):
    geom_corr = np.cos(inc_angle)/primary.dist
    attn_corr = np.exp(-attn_coeff*primary.dist)
    return primary.min/attn_corr/geom_corr*100


# def reflectivity(primary, secondary, attn_coeff, polarity='max'):
#     path_length = 2*np.sqrt(primary.dist**2 + 477**2)
#     geom_corr = np.cos(primary.angle)/path_length
#     attn_corr = np.exp(-attn_coeff*primary.dist)
#     if polarity == 'max':
#         return secondary.max/primary_amp(primary, attn_coeff, inc_angle(primary, inversion_results[0]))/attn_corr/geom_corr
#     elif polarity == 'min':
#         return secondary.min/primary_amp(primary, attn_coeff, inc_angle(primary, inversion_results[0]))/attn_corr/geom_corr


def pair_finder(primary):
    # This function will take a pickfile of primary arrivals and return a list of
    # every primary arrival that has a complementary double pathlength arrival
    dist_tuple_list = []
    index_tuple_list = []
    for dist1 in primary.dist:
        for dist2 in primary.dist:
            if dist2 == dist1*2:
                dist_tuple_list.append((dist1, dist2))
                index_tuple_list.append((np.where(primary.dist == dist1)[0][0], np.where(primary.dist == dist2)[0][0]))
    return index_tuple_list, dist_tuple_list


def pair_source_amplitudes(primary):
    # Find the source amplitude given a primary pickfile
    # This function will take a pickfile of primary arrivals and return a list of
    # estimates of source amplitude from every pair of direct arrivals
    inversion_results = inv1_fit([primary])
    incidence_angle = inc_angle(primary, inversion_results[0])

    index_tuple_list, dist_tuple_list = pair_finder(primary)
    source_amp_list = []
    for i in index_tuple_list:
        path_factor_0 = np.cos(incidence_angle[i[0]])/primary.dist[i[0]]
        path_factor_1 = np.cos(incidence_angle[i[1]])/primary.dist[i[1]]
        source_amp = primary.min[i[0]]**2/primary.min[i[1]] * path_factor_1/(path_factor_0**2)
        source_amp_list.append(source_amp)
    return source_amp_list


def dir_lin_source_amplitudes(primary):
    inversion_results = inv1_fit([primary])
    incidence_angle = inc_angle(primary, inversion_results[0])
    path_factor = np.cos(incidence_angle)/primary.dist
    y = np.log(-primary.min/path_factor)
    x = -primary.dist
    attenuation, logamplitude, r_value, p_value, std_err = sp.stats.linregress(x, y)
    return attenuation, logamplitude, r_value, p_value, std_err