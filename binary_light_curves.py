#!/usr/bin/env python

# Class to generate model binary light curves
# ---
# Abhimat Gautam

import os
import numpy as np
import imf

from phoebe_phitter import isoc_interp, lc_calc

from phoebe import u
from phoebe import c as const

class binary_pop_light_curves(object):
    def  __init__(self):
        # Set up some defaults
        self.set_extLaw_alpha()
        
        return
    
    def make_pop_isochrone(self,
                           isoc_age=4.0e6, isoc_ext_Ks=2.63,
                           isoc_dist=7.971e3, isoc_phase=None,
                           isoc_met=0.0):
        # Store out isochrone parameters into object
        self.isoc_age=isoc_age,
        self.isoc_ext=isoc_ext_Ks,
        self.isoc_dist=isoc_dist,
        self.isoc_phase=isoc_phase,
        self.isoc_met=isoc_met
        
        # Generate isoc_interp object
        self.pop_isochrone = isoc_interp.isochrone_mist(age=isoc_age,
                                                        ext=isoc_ext_Ks,
                                                        dist=isoc_dist,
                                                        phase=isoc_phase,
                                                        met=isoc_met,
                                                        use_atm_func='phoenix')
        
    
    def save_obs_times(self, obs_times_Kp, obs_times_H):
        self.obs_times_Kp = obs_times_Kp
        self.obs_times_H = obs_times_H
    
    def set_extLaw_alpha(self, ext_alpha=2.30):
        self.ext_alpha = ext_alpha
    
    def set_population_extinctions(self, ext_Kp=2.3, ext_H_mod=0.0):
        # Filter properties
        lambda_Ks = 2.18e-6 * u.m
        dlambda_Ks = 0.35e-6 * u.m

        lambda_Kp = 2.124e-6 * u.m
        dlambda_Kp = 0.351e-6 * u.m

        lambda_H = 1.633e-6 * u.m
        dlambda_H = 0.296e-6 * u.m
        
        self.ext_Kp = ext_Kp
        self.ext_H = ext_Kp * (lambda_Kp / lambda_H)**self.ext_alpha + ext_H_mod
        
    
    def set_pop_distance(self, pop_distance=7.971e3):
        self.pop_distance = pop_distance
    
    def make_binary_light_curve(binary_index, mass_1, mass_2,
                                binary_period, binary_t0_shfit,
                                binary_q, binary_ecc, binary_inc,
                                out_dir='./mock_binaries'):
        # Make sure output directory exists
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        
        # Interpolate stellar parameters from isochrone
        (star1_params_all, star1_params_lcfit) = self.pop_isochrone.mass_interp(mass_1)
        (star2_params_all, star2_params_lcfit) = self.pop_isochrone.mass_interp(mass_2)
        
        # Set up binary parameters
        binary_inc = binary_inc * u.deg
        t0 = (np.min(self.obs_times_Kp) - binary_period + binary_t0_shift)

        binary_params_model = (binary_period, binary_ecc, binary_inc, binary_period)
        binary_params = (binary_period * u.d, binary_ecc, binary_inc, t0)
        
        # Set up model times
        model_times = (self.obs_times_Kp, self.obs_times_H)
        
        # Obtain model magnitudes
        num_triangles = 500
        (binary_model_mags_Kp, binary_model_mags_H) = lc_calc.binary_mags_calc(
                                                          star1_params_lcfit,
                                                          star2_params_lcfit,
                                                          binary_params_model,
                                                          model_times,
                                                          self.isoc_ext,
                                                          self.ext_Kp, self.ext_H,
                                                          self.ext_alpha,
                                                          self.isoc_dist * u.pc, self.pop_distance,
                                                          use_blackbody_atm=True,
                                                          num_triangles=num_triangles)