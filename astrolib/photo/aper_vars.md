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
