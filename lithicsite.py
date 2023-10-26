import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import pick_gridsearch as gs

# This script will use picked amplitudes of the primary and secondary seismic
# arrivals to calculate the ratio of the two amplitudes.


pvel = 3800

import pickfile as pf
import pickanalysis as pa


primary_29 = pf.Pickfile('pickdata_lithic/29_primary.info', 'incr', 115, outliers=3)
primary_30 = pf.Pickfile('pickdata_lithic/30_primary.info', 'incr', 115, outliers=3)
primary_31 = pf.Pickfile('pickdata_lithic/31_primary.info', 'incr', 115, outliers=3)
primary_33 = pf.Pickfile('pickdata_lithic/33_primary.info', 'incr', 100, outliers=5)
primary_34 = pf.Pickfile('pickdata_lithic/34_primary.info', 'incr', 100, outliers=5)

secondary_29 = pf.Pickfile('pickdata_lithic/29_secondary.info', 'incr', 'secondary', outliers=3)
secondary_30 = pf.Pickfile('pickdata_lithic/30_secondary.info', 'incr', 'secondary', outliers=3)
secondary_31 = pf.Pickfile('pickdata_lithic/31_secondary.info', 'incr', 'secondary', outliers=3)
secondary_33 = pf.Pickfile('pickdata_lithic/33_secondary.info', 'incr', 'secondary', outliers=5)
secondary_34 = pf.Pickfile('pickdata_lithic/34_secondary.info', 'incr', 'secondary', outliers=5)

# aquifer_primary_list = [primary_72, primary_73, primary_74, primary_76, primary_77, primary_78, primary_79, primary_80, primary_81, primary_82]

primary_lithic_fullstack = pf.Pickfile('pickdata_lithic/fullstack_stacked_primary.info', 'incr', 0, 3, maxrows=24)

# secondary_74 = pf.Pickfile('pickdata_aquifer/74_wind_secondary.info', 'incr', 195)
# secondary_73 = pf.Pickfile('pickdata_aquifer/73_wind_secondary.info', 'incr', 195)
# secondary_72 = pf.Pickfile('pickdata_aquifer/72_wind_secondary.info', 'incr', 195)
# secondary_76 = pf.Pickfile('pickdata_aquifer/76_wind_secondary.info', 'incr', midsouth)
# secondary_77 = pf.Pickfile('pickdata_aquifer/77_wind_secondary.info', 'incr', midsouth)
# secondary_78 = pf.Pickfile('pickdata_aquifer/78_wind_secondary.info', 'incr', midspread)
# secondary_79 = pf.Pickfile('pickdata_aquifer/79_wind_secondary.info', 'incr', midspread)
# secondary_80 = pf.Pickfile('pickdata_aquifer/80_wind_secondary.info', 'incr', 60, 3)
# secondary_81 = pf.Pickfile('pickdata_aquifer/81_wind_secondary.info', 'incr', 60, 3)
# secondary_82 = pf.Pickfile('pickdata_aquifer/82_wind_secondary.info', 'incr', 60, 3)
secondary_lithic_fullstack = pf.Pickfile('pickdata_lithic/fullstack_stacked_secondary.info', 'incr', 0, 3, maxrows=24)




attn_opt, attn_cov = pa.attn_fit([primary_lithic_fullstack])
# Next we'll fit attenuation using picks from the shot_loc_data_primary array
# attn_opt_new, attn_cov = attn_fit(shot_loc_data_primary)


# def primary_amp(primary, attn_coeff, inc_angle):
#     geom_corr = np.cos(inc_angle)/primary.dist_no_outliers
#     attn_corr = np.exp(-attn_coeff*primary.dist_no_outliers)
#     return primary.min_no_outliers/attn_corr/geom_corr*100
def primary_amp(primary, attn_coeff, inc_angle):
    geom_corr = np.cos(inc_angle)/primary.dist
    attn_corr = np.exp(-attn_coeff*primary.dist)
    return primary.min/attn_corr/geom_corr*100


inversion_results = pa.inv1_fit([primary_lithic_fullstack])
# incidence_angle = inc_angle(primary_fullstack, inversion_results[0])
incidence_angle = pa.inc_angle(primary_lithic_fullstack, inversion_results[0])

depth, vel = pa.inv1_depth(np.arange(0, 200, 0.1), inversion_results[0])
np.save('tmp/depthvel_lithic.npy', np.array([depth, vel]))
plt.plot(vel, depth)
plt.ylim([0, 40])
plt.gca().invert_yaxis()
plt.show()


def reflectivity(primary, secondary, attn_coeff, polarity='max'):
    path_length = 2*np.sqrt(primary.dist**2 + 477**2)
    geom_corr = np.cos(primary.angle)/path_length
    attn_corr = np.exp(-attn_coeff*primary.dist)
    if polarity == 'max':
        return secondary.max/primary_amp(primary, attn_coeff, pa.inc_angle(primary, inversion_results[0]))/attn_corr/geom_corr
    elif polarity == 'min':
        return secondary.min/primary_amp(primary, attn_coeff, pa.inc_angle(primary, inversion_results[0]))/attn_corr/geom_corr


ref_29 = reflectivity(primary_29, secondary_29, attn_opt[0], polarity='min')
ref_30 = reflectivity(primary_30, secondary_30, attn_opt[0], polarity='min')
ref_31 = reflectivity(primary_31, secondary_31, attn_opt[0], polarity='min')
ref_lithic_stack = reflectivity(primary_lithic_fullstack, secondary_lithic_fullstack, attn_opt[0], polarity='min')
# ref_stack = reflectivity(primary_stack, secondary_stack, attn_opt[0])
ref_all = []
for i in range(len([primary_lithic_fullstack])):
    ref_temp = np.array(reflectivity([primary_lithic_fullstack][i], [secondary_lithic_fullstack][i], attn_opt[0]))
    ref_all.append(ref_temp)


# # Plot reflectivity as a function of angle
plt.scatter(np.rad2deg(primary_29.angle), ref_29, zorder=1, s=20)
plt.scatter(np.rad2deg(primary_30.angle), ref_30, zorder=1, s=20)
plt.scatter(np.rad2deg(primary_31.angle), ref_31, zorder=1, s=20)
plt.scatter(np.rad2deg(primary_lithic_fullstack.angle), ref_lithic_stack, zorder=1, s=20)
# # plt.legend(['29', '30', '31'])
# plt.ylim([-0.5, 1])
plt.title('Reflectivity as fxn of angle')
plt.ylabel('Reflectivity')
plt.xlabel('Angle (deg)')
plt.grid()
plt.show()


def refl_time(offset, angle, velocity, depth=405):
    refl_timing = 2*np.sqrt(
                            (depth ** 2) +
                            ((offset/2)**2 * np.cos(np.deg2rad(angle))**2)
    ) / velocity
    return refl_timing

def zerodip_depth(reflectiontiming, offset, velocity):
    return np.sqrt((reflectiontiming*velocity/2)**2 - (offset/2)**2)
# Plot theoretical correct time difference between primary and secondary
# We'll do this using the primary arrival travel time curve generated by the inversion
refl_tdiff = np.array([])
refl_tdiff_inv = np.array([])
refl_timingarray_0deg = np.array([])
refl_timingarray_10deg = np.array([])
refl_timingarray_20deg = np.array([])
refl_deep = np.array([])
for i in range(1, 200, 1):
    # refl_timing = 2*np.sqrt(i**2 + 405**2)/3830
    refl_timingarray_0deg = np.append(refl_timingarray_0deg, refl_time(i, 0, 3600, 405))
    refl_timingarray_10deg = np.append(refl_timingarray_10deg, refl_time(i, -10, 3600, 405))
    refl_timingarray_20deg = np.append(refl_timingarray_20deg, refl_time(i, -20, 3600, 405))
    # refl_tdiff = np.append(refl_tdiff, refl_time(i, 0, 3600, 405) - i/3600)
    refl_deep = np.append(refl_deep, refl_time(i, 0, 3710, 477))
    # refl_tdiff_inv = np.append(refl_tdiff_inv, refl_timing - inv1(i, inversion_results[0][0], inversion_results[0][1],
    # inversion_results[0][2], inversion_results[0][3], inversion_results[0][4]))

# # Plot data vs theoretical reflection traveltime
# # plt.plot(primary_stack.dist, secondary_stack.tmin)
# #plt.plot(primary_stack.dist, secondary_stack.tmax)
# plt.plot(primary_72.dist, secondary_72.tmax)
# plt.plot(primary_73.dist, secondary_73.tmax)
# plt.plot(primary_74.dist, secondary_74.tmax)
# plt.plot(primary_76.dist, secondary_76.tmax)
# plt.plot(primary_77.dist, secondary_77.tmax)
# plt.plot(primary_78.dist, secondary_78.tmax)
# plt.plot(primary_79.dist, secondary_79.tmax)
# plt.plot(primary_80.dist, secondary_80.tmax)
# plt.plot(primary_81.dist, secondary_81.tmax)
# plt.plot(primary_82.dist, secondary_82.tmax)
# plt.plot(np.arange(1,200,1), refl_timingarray_0deg, zorder=0)
# plt.plot(np.arange(1,200,1), refl_timingarray_10deg, zorder=0)
# plt.plot(np.arange(1,200,1), refl_timingarray_20deg, zorder=0)
# # plt.legend(['Data', 'Theoretical'])
# plt.title('Data vs theoretical reflection traveltime')
# # plt.legend(['Shot 1', 'Shot 2', 'Shot 3', '0 deg bed', '10 deg bed', '20 deg bed'])
# plt.xlabel('Offset (m)')
# plt.ylabel('Traveltime (s)')
# plt.show()

# # Plot zero dip reflector depth
# plt.title('Reflector depth assuming zero reflector dip')
# #plt.plot(primary_stack.dist/2, zerodip_depth(secondary_stack.tmin, secondary_stack.dist, 3800))
# plt.plot(primary_73.dist/2, zerodip_depth(secondary_73.tmax, secondary_73.dist, 3650))
# plt.plot(primary_74.dist/2, zerodip_depth(secondary_74.tmax, secondary_74.dist, 3650))
# plt.ylim(400, 450)
# plt.show()


# # Plot direct arrival time vs offset
primary_known_slope, primary_known_intercept = sp.stats.linregress(primary_lithic_fullstack.tmin, primary_lithic_fullstack.dist)[0:2]

plt.scatter(primary_lithic_fullstack.dist, primary_lithic_fullstack.tmin, s=50, marker="o", zorder=0, facecolors='none', edgecolors='k')
# plt.plot(np.arange(0,0.06,0.001)*primary_known_slope+primary_known_intercept, np.arange(0,0.06,0.001), zorder=0, linewidth=0.5)
plt.plot(np.arange(0, 125, 200), pa.inv1(np.arange(0, 125, 200), *inversion_results[0]), zorder=0, linewidth=0.5)
plt.title('Direct arrival time vs offset')
plt.xlabel('Offset (m)')
plt.ylabel('Traveltime (s)')
plt.show()

# Plot traveltime of lithic reflector vs offset
plt.plot(primary_lithic_fullstack.dist_no_outliers, secondary_lithic_fullstack.tmin_no_outliers)
plt.plot(primary_29.dist_no_outliers, secondary_29.tmin_no_outliers)
plt.plot(primary_30.dist_no_outliers, secondary_30.tmin_no_outliers)
plt.plot(primary_31.dist_no_outliers, secondary_31.tmin_no_outliers)
plt.plot(primary_33.dist_no_outliers, secondary_33.tmin_no_outliers)
plt.plot(primary_34.dist_no_outliers, secondary_34.tmin_no_outliers)
plt.xlabel('Offset (m)')
plt.ylabel('Traveltime (s)')
plt.plot(np.arange(1,200,1), refl_deep, zorder=0)
plt.show()

gs.depthvel_gridsearch_plot([primary_lithic_fullstack], [secondary_lithic_fullstack], prior=[3710, 477])
