import scipy.integrate as integrate
import numpy
from math import *


omega_m=0.3
omega_l=.7
omega_k=  1. - omega_m - omega_l
H_0 = 70.
h=H_0/100.
c = 2.998e5
dh=c/H_0
th=1./H_0
th=9.78e9/h

def e_inverse(z):
    v=1./(sqrt(omega_m*(1+z)**3 + omega_k*(1+z)**2 + omega_l))
    return v

def e_inverset(z):
    v=1./((1.+z)*sqrt(omega_m*(1+z)**3 + omega_k*(1+z)**2 + omega_l))
    return v

def cosmo(z,type,dz=0.,unit=None):

    if unit is None: fact=1.
    if unit is 'cm':
        fact=3.0856*1e18*1e6




    if type=='dc':
        integ=integrate.quad(e_inverse,0.00001,z)[0]
        return dh*integ

    elif type == 'dm':

        if omega_k == 0.:
            return cosmo(z,'dc')
        if omega_k > 0.:
            return dh*(1./sqrt(omega_k))*sinh(sqrt(omega_k)*cosmo(z,'dc')/dh)
        if omega_k < 0.:
            return dh*(1./sqrt(abs(omega_k)))*sin(sqrt(abs(omega_k))*cosmo(z,'dc')/dh) 

    elif type == 'da':
        return fact*cosmo(z,'dm')/(1+z)


    elif type == 'dl':
        return fact*cosmo(z,'dm')*(1+z)

    elif type == 'dzdr':
        return cosmo((z+dz/2),'dc')-cosmo((z-dz/2),'dc')
    
    elif type == 'dvc':
        return omega*d_z*dh*(1+z)^2.*(cosmo(z,'da'))**2. * e_inverse(z)

    elif type == 'lbt':
        return th*integrate.quad(e_inverset,0.00001,z)[0]
