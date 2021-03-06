import numpy as np
from astropy.wcs import WCS
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy import units as u

def load_file(inpfile):
    dat, hdr = fits.getdata(inpfile, header=True)
    wcs = WCS(hdr)
    return dat,wcs

def get_wave_arr(dat,hdr,extract_wcs=True):
    if extract_wcs is True:
        wcs = WCS(hdr)
    else:
        wcs = hdr
    try:
        wdelt = wcs.wcs.pc[-1,-1]
        #wdelt = hdr['PC3_3']
    except:
        wdelt = wcs.wcs.cd[-1, -1]
        #wdelt = hdr['CD3_3']
    dim = np.shape(dat)
    lastwaveidx = dim[0] - 1
    w1 = wcs.wcs_pix2world([[0, 0, 0]], 1)[0][2]
    w2 = wcs.wcs_pix2world([[0, 0, lastwaveidx]], 1)[0][2]

    newwavearr = np.arange(w1, w2+wdelt, wdelt)
    if round(newwavearr[-1],1)>round(w2,1):
        newwavearr=newwavearr[:-1]
    #if len(newwavearr)!=len(dat)
    return newwavearr

def bright_pix_coords(cube,wcs=None,pixrange=None,waverange=None):
    from kcwi_jnb.cube import DataCube
    if isinstance(cube, DataCube):
        image = cube.data
        wcs = cube.wcs
    else:
        image = cube
    if pixrange is None:
        maxref = np.max(image)
    else:
        maxref = np.max(image[pixrange[0]:pixrange[1], pixrange[2]:pixrange[3]])
    maxrefpix = np.where(image == maxref)

    ### Indices are returned in Y,X order and are zero indexed where pixels
    ### start with 1 in the FITS standard
    try: # Weird array shape issue, possibly a Python 3 thing?
        maxrefcoords = wcs.wcs_pix2world(maxrefpix[1][0] + 1, maxrefpix[0][0] + 1, 1)
    except:
        maxrefcoords = wcs.wcs_pix2world(maxrefpix[1] + 1, maxrefpix[0] + 1, 1)
    maxrefcoords = SkyCoord(maxrefcoords[0], maxrefcoords[1], unit='deg')

    return maxrefpix,maxrefcoords


def dist_from_center(cube,pix='all',center=None,physical=True,z=0.6942):
    if center is None:
        center  = SkyCoord(189.08277646, 62.21439961,unit='deg')
    if pix == 'all':
        cubedims = np.shape(cube.data)
        distarr = np.zeros((cubedims[1],cubedims[2]))
        for i,yy in enumerate(np.arange(cubedims[1])):
            for j,xx in enumerate(np.arange(cubedims[2])):
                pixcoords = cube.wcs.wcs_pix2world([[xx+1 , yy+1 , 1]], 1)
                ccpobj = SkyCoord(pixcoords[0][0], pixcoords[0][1], unit='deg')
                sep = center.separation(ccpobj)
                distarr[i,j] = sep.to(u.arcsec).value
        return distarr
    else:
        pixcoords = cube.wcs.wcs_pix2world([[pix[1][0] + 1, pix[0][0] + 1, 1]], 1)
        ccpobj = SkyCoord(pixcoords[0][0], pixcoords[0][1], unit='deg')
        sep = center.separation(ccpobj)
        return sep


