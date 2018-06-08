"""
This module contains functions for displaying progress and timing of operations.
"""

from    __future__  import absolute_import
from    __future__  import division
from    __future__  import print_function
from    __future__  import unicode_literals

from   .__imports__ import *

##  ========================================================================  ##

def progress( i, length, step=1, alert=None, tabs=0 ):
    """
    Display progress in percentile for any iterated process.
    """

    ## Print alert on first iteration.

    if i == 0 and alert is not None:

        print( alert )

    elif i == length-1:

        print( 70 * " ", end="\r" )
        sys.stdout.flush()

    elif i % step < 0.001:

        ## Print progress bar and display percentage.

        complete    = i / length
        bar         = int( 20 * complete ) * "=" + ">"
        space       = ( 20 - len(bar) ) * " "
        line        = "[" + bar + space + "]   {:.1%}".format( complete )

        print( line, end="\r" )
        sys.stdout.flush()

##  ========================================================================  ##

class Timer:
    """
    The Timer class consists of a dictionary of timers.  Timer initializes the
    dictionary with the key "net" which starts a time.clock().  Intermediate
    processes may be timed by adding an element to the dictionary with the
    methods <Timer>.start( "process_name" ) and <Timer>.end( "process_name" )
    upon which the time from start to end is printed to the terminal.  The net
    time of <Timer> is printed upon the call <Timer>.close().
    """

    def __init__( self, alert=None ):

        self.timers     = { "net": time.clock() }       # "timer_name": time_0

        if alert is not None:

            print( alert )
            sys.stdout.flush()

    def start( self, timer_name, alert=None ):

        self.timers[ timer_name ] = time.clock()

        if alert is not None:

            print( alert )
            sys.stdout.flush()

    def end( self, timer_name, alert=None ):

        if alert is not None:

            print( alert )
            sys.stdout.flush()

        dt = ( time.clock() - self.timers[ timer_name ] ) / 60

        print( "Time: %.2f minutes." % dt )
        sys.stdout.flush()

    def alert( self, alert, start="", end="" ):

        print( start + alert + end )
        sys.stdout.flush()

    def close( self, alert=None, end="" ):

        if alert is not None:

            print( alert )

        Dt = ( time.clock() - self.timers[ "net" ] ) / 60

        print( "Net Time: %.2f minutes." % Dt + end )
sys.stdout.flush()
