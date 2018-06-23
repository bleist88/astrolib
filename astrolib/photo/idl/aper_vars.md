##  aper.pro variables

s           = image size
ncol        = number of columns in image
nrow        = number of rows in image

badpix      = [ bad pixel values, ]

apr         = [ aperture radii, ]
skyrad      = [ annulus radii, ]

Naper       = number of apertures
Nstar       = number of stars

area        = analytical area of each aperture ( pi * r**2 )
bigrad      = apr + 0.5
smallrad    = apr/sqrt(2) - 0.5

rinsq       = inner annulus radius squared
routsq      = outer annulus radius squared

rotobuf     = stamp cutout
rsq         = squared radial distance of each pixel
r           = radial distance of each pixel - 0.5
skybuf      = annulus selection of rotobuf

fractn      = aperture radius - radius to pixel (to the near edge of pixel)
full        = [ 1 where fractn == 1.0, 0 where fractn != 1.0 ]
gfull       = where full == 1
Nfull       = the number of full == 1
gfract      = where full == 0
factor      = (area - Nfull) / sum( fractn[gfract] )

thisapd     = data in aperture

skysig      = clipped sky std
skyvar      = clipped sky var = std**2
sigsq       = clipped mean sky var  (skyvar / nsky)

err_sky     = area * sky_std**2
err_sky     = area**2 * sky_sig**2
err_php     = mag / php
err_zero    = mag zeropoint error

1.  What aperture and annulus radii?

2.  Running IDL code.

3.  IDL calculates total_aperture_area / total_fractional_area.  Should I
    calculate using fractional area per pixel?

4.  The EXACT argument calculates the overlap of circle to pixel.

5.  Error analysis:

    1.  random photon noise:    flux / php_adu
    2.  mean sky uncertainty:   ap_area**2 * (sky_var / an_area)
    3.  sky scatter:            ap_area * sky_var

    err_total   = sqrt( e1**2 + e2**2 + e3**2 ) --> magnitude

    err_total   = sqrt( error_total**2 + err_zero**2 )

6.  Magnitudes in aper.pro are defined by a magnitude zeropoint of 25.0.  The
    keyword /FLUX can be provided to specify the flux unit in the image.
