"""
This file contains tools used for improving plots.
"""


from    __future__      import absolute_import
from    __future__      import division
from    __future__      import print_function
from    __future__      import unicode_literals

from   .__imports__     import *

##  ============================================================================

def smart_figure( fig, aspect="auto" ):

    fig.tight_layout()

    for i in range( len(fig.axes) ):

        fig.axes[i].minorticks_on()

        fig.axes[i].tick_params(
            axis        = "both",
            which       = "major",
            direction   = "inout",
            length      = 12,
            width       = 1.2,
        )

        fig.axes[i].tick_params(
            axis        = "both",
            which       = "minor",
            direction   = "inout",
            length      = 7,
            width       = 1.2,
        )

        fig.axes[i].set_aspect( aspect )
