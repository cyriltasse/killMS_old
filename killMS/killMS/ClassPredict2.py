import numpy as np


def giveGauss(u,v,e_maj,e_min,pa,freq):
    # ok, get the shape attributes

    C=2.99792456e8


    el    = e_maj*np.sin(pa)
    em    = e_maj*np.cos(pa)
    ratio = e_min/e_maj

    fwhm2int = 1.0/np.sqrt(np.log(16.0))
    # ok, so the projections of the major axis onto the l/m axes are el and em
    # from this we can work out cos(PA) and sin(PA)
    fwhm = np.sqrt(el**2+em**2)
    cos_pa = em/fwhm
    sin_pa = el/fwhm
    
    # rotate uv-coordinates through PA to put them into the coordinate frame
    # of the gaussian
    u1 = cos_pa*u - sin_pa*v
    v1 = sin_pa*u + cos_pa*v

    # scale uv-coordinates by the extents
    # fwhm computed above is the extent along the m axis (extent along v is reciprocal)
    # fwhm*ratio is the extent along the l axis (extent along u is reciprocal)
    # we need to DIVIDE u1 and v1 by the uv-extents, thus we multiply by the lm-extents
    # instead, and divide by the reciprocality constant
    
    # but first, we convert FWHM to uv-space 
    # ok the extra 4pi is just a fudge here, 
    # until I figure out WTF is the right scale, but this gives suspiciously correct results
    # AGW added an extra ln(2)
    scale_uv = 1/(fwhm*fwhm2int*np.pi*np.pi*4.0*np.log(2.))
    scale_uv *= freq/C; # (fwhm2int/C::c)*freq_vells_;
    print scale_uv
    # apply extents to u1 and v1
    u1 /= scale_uv/ratio
    v1 /= scale_uv
    
    #K = np.exp(-(u1**2+v1**2))
    K = -(u1**2+v1**2)

    return K
