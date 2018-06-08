"""
PyFits/Cleaner.py
"""

from .__imports__ import *

################################################################################

class Cleaner():
    """
    This class assists in converting backtype values, placing masks, and
    resizing FITS images.
    """

    def __init__( self, fits_file ):

        self.file_name      = fits_file
        self.data           = fits.getdata( fits_file )
        self.header         = fits.getheader( fits_file )
        self.shape          = np.shape( self.data )
        self.backtype       = self.data[1,1]

    ############################################################################

    def save( self, file_name, clobber=False ):
        """
        Save the FITS file.  If overwriting, set 'clobber=True'.
        """

        if file_name == self.file_name and clobber is False:

            print(
                "Could not overwrite %s because 'clobber=False'.  To " \
                "overwrite a FITS file, set 'clobber=True' " % file_name
            )

        else:

            hdu     = fits.PrimaryHDU( self.data, header=self.header )
            hdu.writeto( file_name, clobber=True )

    ############################################################################

    def set_backtype( self, backtype ):
        """
        Convert the back values to the specified backtype.
        """

        ## Converting to NaN.

        if backtype in ['NAN','NaN','Nan','nan']:

            temp_data       = np.copy( self.data )

            for i in range( 1, len(self.data)-1 ):

                ## Ensure only non-isolated values of 0 are set to NaN and
                ## convert previous 0s to NaN.

                backs       = np.where( self.data[i] == 0.0 )[0]
                backs_a     = np.where( self.data[ i-1, backs ] == 0.0 )[0]
                backs_b     = np.where( self.data[ i+1, backs ] == 0.0 )[0]

                temp_data[ i, backs[backs_a] ]  = np.nan
                temp_data[ i, backs[backs_b] ]  = np.nan

            temp_data[ 0 ]      = np.nan
            temp_data[ -1 ]     = np.nan

            ## Overwrite.

            self.data           = temp_data
            self.backtype       = backtype

        ## Convert to 0s.

        else:

            ## Find NaN values and replace them.

            for i in range(len( self.data )):

                nans                    = np.where( np.isnan(self.data[i]) )[0]
                self.data[ i, nans ]    = backtype
                self.backtype           = backtype

    ############################################################################

    def cut_min( self, min_val ):
        """
        Set values outside of the limits to backtype value.
        """

        a   = np.where( self.data < min_val )

        self.data[ a ]  = self.backtype

    def cut_max( self, max_val ):
        """
        Set values outside of the limits to backtype value.
        """

        a   = np.where( self.data > max_val )

        self.data[ a ]  = self.backtype

    ############################################################################

    def crop( self, width ):
        """
        Crop the overall FITS image by fixed pixel amount.
        """

        # Crop the full image in by a desired amount.

        self.header["CRPIX1"]   -= width
        self.header["CRPIX2"]   -= width

        ##  WTF was this?
        #subs            = np.copy( self.data[ width:-width, width:-width ] )
        #self.data      *= self.backtype
        #self.data[ width:-width, width:-width ]     = subs

        self.data   =   self.data[ width:-width, width:-width ]

    ############################################################################

    def trim_boarder( self, width ):
        """
        Move the boarder pixels into the data by a fixed width.
        """

        ## Convert backtype values to NaN if not already.

        nantype = None

        if not np.isnan( self.data[ 1,1 ] ):
            nantype = self.data[ 1,1 ]
            self.set_backtype( 'NaN' )
        else:
            nantype = self.data[ 1,1 ]

        ## Create a matrix of all ones of the data.
        ## Shift NaNs in all directions to move boarder NaNs into the data.

        unit            = ( self.data + np.pi ) / ( self.data + np.pi )

        self.data[ 0:-width, 0:-width ]   *= unit[ width:, width: ]
        self.data[ width:, width: ]       *= unit[ 0:-width, 0:-width ]

        # Revert back to the original backtype.

        if nantype is not None:

            self.set_backtype( nantype )

    ############################################################################

    def trim_radially( self, radius ):
        """
        Set all values outside of specified radius from the center to the
        backtype.
        """

        # Find center pixels.

        x0      = self.shape[0] / 2     # self.header['CRPIX1']
        y0      = self.shape[1] / 2     # self.header['CRPIX2']

        # Create meshgrid of data.

        X       = np.arange( self.shape[0] )
        Y       = np.arange( self.shape[1] )
        X, Y    = np.meshgrid( X, Y )

        #i = np.tile(
        #    np.arange( self.shape[0] ), (self.shape[1],1)
        #    ).T
        #j = np.tile(
        #    np.arange( self.shape[1] ), (self.shape[0],1)
        #    )

        # Set all values with large radius to the back value.

        self.data[
            np.where(
                (X-x0)**2 + (Y-y0)**2 > radius**2
            )
        ] = self.backtype

    ############################################################################

    def mask( self, x0, y0, radius ):
        """
        Mask all values within specified radies of specified point (x0,y0).
        """

        # Create meshgrid of data.

        X       = np.arange( self.shape[0] )
        Y       = np.arange( self.shape[1] )
        X, Y    = np.meshgrid( X, Y )

        # Set all values with large radius to the back value.

        self.data[
            np.where(
                (X-x0)**2 + (Y-y0)**2 < radius**2
            )
        ] = self.backtype

################################################################################

def clean(
    fits_file, saveas=None,
    backtype=0.0, min_val=-10000, max_val=10000, trim=0, crop=0
):

    aCleaner    = Cleaner( fits_file )

    ##  Clean.

    aCleaner.set_backtype( backtype )

    aCleaner.cut( min_val=min_val, max_val=max_val )

    if trim > 0:

        aCleaner.trim_boarder( trim )

    if crop > 0:

        aCleaner.crop( crop )

    ##  Save.

    if saveas is None:

        aCleaner.save( fits_file, clobber=True )

    else:

        aCleaner.save( saveas )
