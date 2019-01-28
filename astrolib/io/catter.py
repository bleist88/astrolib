"""
This file contains the class Catter.  This class allows for interactive viewing
of an ascii catalog by plotting histograms of column data and allows for cutting
data away.
"""

from ._imports import *

##  ========================================================================  ##

class catter:
    """
    A class to view catalog data.  This class plots histograms of selected
    arrays within a catalog as well as modifies the data.
    """

    def __init__( self, file_name, dtype=None, ion=True ):

        ## Read the data.

        self.data           = io.read( file_name, dtype=dtype )
        self.dtype          = self.data.dtype

        ## History.

        self.original       = np.arange( len(self.data) )
        self.indices        = np.copy( self.original )
        self.removed        = float( len(self.indices) ) / len(self.data)
        self.history        = []

        ## Distribution.

        self.parameter      = None
        self.distribution   = None

        ## Statistics.

        self.mean           = None
        self.median         = None
        self.mode           = None
        self.std            = None
        self.rms            = None

        ## Matplotlib.

        if ion is True:
            pyplot.ion()

    ##########################################   B A S I C   O P E R A T I O N S

    def update( self, bins=50 ):
        """
        Update the stats and plot.
        """

        if self.parameter != None:

            self.mean       = np.mean( self.distribution )
            self.median     = np.median( self.distribution )
            self.mode       = 3 * self.median - 2 * self.mean
            self.std        = np.std( self.distribution )
            self.rms        = self.std**2

            self.hist( bins=bins )

    def restore( self ):
        """
        Undo all changes made to the array.
        """

        self.indices    = np.copy( self.original )

        if self.parameter != None:

            self.distribution = self.data[self.original][self.parameter]

        self.update()

    def undo( self ):
        """
        Return data to status before previous operation.
        """

        if len( self.history ) > 0:

            self.indices        = self.history[-2]
            self.distribution   = self.data[self.indices][self.parameter]
            self.update()
            del self.history[-1:]

    def write( self, file_name, clobber=True ):
        """
        Write data to a formatted ascii catalog.  If keep=True, this will write
        the new array to a file starting with 'cut_' so that the original file
        is not overwritten.
        """

        io.write( file_name, self.data[self.indices] )

        if clobber == False:

            io.write( 'cut_' + file_name, np.delete(self.data,self.indices) )

    def display( self ):
        """
        Display the selected array's statistics to the terminal.
        """

        if self.parameter == None:
            raise NameError("No array was selected.")

        print()
        print( 'Parameter:  %s'     % self.parameter )
        print( 'Mean:       %.2f'   % self.mean )
        print( 'Median:     %.2f'   % self.median )
        print( 'Mode:       %.2f'   % self.mode )
        print( 'Deviation:  %.2f'   % self.std )
        print()

    ######################################   A R R A Y   M O D I F I C A T I O N

    def select( self, parameter ):
        """
        Select a parameter column in which to operate and display.
        """

        self.parameter      = parameter
        self.distribution   = self.data[self.indices][self.parameter]
        self.update()

    def new_space( self, new_array, parameter ):
        """
        Create a new space.
        """

        self.parameter      = parameter
        self.distribution   = new_array
        self.update()

    def cut_min( self, value ):
        """
        Cut all elements below specified value from the distribution.
        """

        cuts                    = np.where( self.distribution >= value )[0]
        self.distribution       = self.distribution[ cuts ]
        self.indices            = self.indices[ cuts ]
        self.history.append( self.indices )
        self.update()

    def cut_max( self, value ):
        """
        Cut all elements above specified value from the distribution.
        """

        cuts                    = np.where( self.distribution <= value )[0]
        self.distribution       = self.distribution[ cuts ]
        self.indices            = self.indices[ cuts ]
        self.history.append( self.indices )
        self.update()

    def cut( self, minimum, maximum ):
        """
        Cut all elements outside of specified range.
        """

        if minimum < maximum:
            self.cut_min( minimum )
            self.cut_max( maximum )

        elif minimum > maximum:
            self.cut_min( maximum )
            self.cut_max( minimum )

    ##########################################################   P L O T T I N G

    def hist( self, bins=50 ):
        """
        Plot a histogram of the distribution.
        """

        ## Ensure a parameter is selected.

        if self.parameter is None:

            raise NameError("A parameter must be selected to plot.")

        ## Plot a histogram of the selected distribution.

        pyplot.close()
        h_fig       = pyplot.figure()
        h_axes      = h_fig.add_subplot( 1,1,1 )

        ## Statistics.

        #mode_x    = ( self.mode, self.mode )
        #mode_y    = ( self.mode-self.std, self.mode+self.std )
        #h_axes.plot( mode_x, mode_y, 'g--' )

        ## Histogram

        h_axes.set_xlabel( self.parameter )

        h_axes.hist(
            self.distribution, bins,
            normed=True, histtype='step', color='k',
            label='%i  Objects' % len(self.distribution)
        )

        h_axes.legend( loc='best', frameon=False )
