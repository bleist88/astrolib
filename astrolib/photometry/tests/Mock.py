
##  This will eventually be a module within Photopy, but for now it is just a
##  way of testing the photometry on perfect point sources created in this
##  script.

import numpy as np

x0, y0      = 0, 0
x1, y1      = 33, 10
x2, y2      = -17, -15
x3, y3      = 36, -45

f0          = 5
f1          = 20
f2          = 8
f3          = 15

std0        = 1
std1        = 3
std2        = 4
std3        = 2

sky         = .007
sky_std     = .2 * sky

def make_star( stamp, x, y, total, std ):

    radial  = np.sqrt(
        (stamp.grid[0] - stamp.pix_x - x)**2 +
        (stamp.grid[1] - stamp.pix_y - y)**2
    )

    star    = np.exp( -.5 * (radial / std)**2 )
    star   *= total / np.sum( star )

    return  star

def mock( stamp, seeing ):

    star0   = make_star( stamp, x0, y0, f0, seeing + std0 )
    star1   = make_star( stamp, x1, y1, f1, seeing + std1 )
    star2   = make_star( stamp, x2, y2, f2, seeing + std2 )
    star3   = make_star( stamp, x2, y2, f3, seeing + std3 )

    stamp.data   *= 0.0
    sky_data      = np.random.normal( loc=sky, scale=sky_std, size=stamp.shape )
    stamp.data   += sky_data + star0 #+ star1 + star2 + star3

def mock_true( stamp, seeing ):

    star0   = make_star( stamp, x0, y0, f0, seeing + std0 )
    stamp.data  = 0.0
    stamp.data  += star0
