"""
This file houses the managers used to manage the field, data, filters and SEDs.
"""

from ._imports import *

##  ============================================================================

##  Define the master catalog dtype.

master_dtype    = {
    "names":    [
        "id",  "matches", "alpha", "delta", "Rc", "S"
    ],
    "formats":  [
        "int64", "int64", "float64", "float64", "float64", "float64"
    ]
}

##  ============================================================================

class master:

    def __init__( self, file_name, init=False ):

        ##  Members

        self.file_name      = file_name
        self.fits_cube      = None

        self.master         = np.zeros( 0, dtype=master_dtype )
        self.N              = 0
        self.alpha          = None
        self.delta          = None

        self.catalogs       = {}
        self.Rc             = {}

        ##  Initialization.

        if init is True:
            self.init_fits( file_name )
        elif init is False:
            self.open( self.file_name )
        else:
            raise   Exception("'init' must be set to either 'True' or 'False'.")

    def display( self ):
        """
        Display attributes into the terminal.
        """
        print( self.file_name                           )
        print( "       N:      ",  self.N               )
        print( "   alpha:      ",  self.alpha           )
        print( "   delta:      ",  self.delta           )
        print(                                          )
        print( "catalogs:      ",  len(self.catalogs)   )
        print( "       1:      ",  "master"             )
        for i, cat in enumerate( self.catalogs ):
            print( "       ", i+2, "    ", cat          )
        print(                                          )

    ##  ========================================================================
    ##  File Management

    def open( self, file_name ):
        """
        Set all class members from the master fits cube meta data and catalog
        extension data.
        """

        ##  Open the fits cube.

        self.fits_cube  = fits.open( file_name )

        ##  Retrieve meta data and master catalog.

        self.master     = self.fits_cube["master"].data
        self.N          = self.fits_cube["master"].data.size
        self.alpha      = self.fits_cube["master"].header["alpha"]
        self.delta      = self.fits_cube["master"].header["delta"]

        ##  Retrieve all extensions.

        for i in range( 2, len(self.fits_cube) ):

            cat                     = self.fits_cube[i].header["EXTNAME"]
            self.catalogs[ cat ]    = self.fits_cube[i].data
            self.Rc[ cat ]          = self.fits_cube[i].header["Rc"]

    def save( self, saveas=None, overwrite=False ):
        """
        Saves the object to a FITS cube.

        Arguments:
            saveas=None     - file path to save to; if None, uses existing path
            overwrite=False - if overwrite=True, overwrites existing file paths
        """

        ##  Set the master catalog extension.

        self.fits_cube["master"].header.set( "N",       self.N      )
        self.fits_cube["master"].header.set( "alpha",   self.alpha  )
        self.fits_cube["master"].header.set( "delta",   self.delta  )

        ##  Set all catalog extension data and headers.

        for cat in self.catalogs:

            self.fits_cube[ cat ].data      = self.catalogs[cat]
            self.fits_cube[ cat ].header.set( "Rc", self.Rc[cat] )

        ##  Write to the fits cube.

        self.fits_cube.writeto( self.file_name, overwrite=overwrite )

    def init_fits( self, file_name ):
        """
        Initialize a FITS file to store the master catalog cube.  The 0th
        extension contains no useful information.  The 1st extension contains
        the global meta data information in the header (N, alpha, delta) and the
        master catalog array in binary table format.  The remaining extensions
        are the correlated catalog arrays in binary table format.  Any catalog
        extension can be accessed via its index in the cube or by catalog name.

        Arguments:
            file_name       - file path to write to
            overwrite=False - if True, overwrites existing file path
        """

        ##  Initialize the FITS object.

        primary_ext     = fits.PrimaryHDU( np.zeros((10,10)) )
        primary_ext.header.set( "EXTNAME", "primary")

        master_ext      = fits.BinTableHDU.from_columns( self.master )
        master_ext.header.set( "EXTNAME", "master" )

        hdu_list        = fits.HDUList( [primary_ext, master_ext] )

        ##  Write info to the fits header.

        hdu_list["master"].header.set( "N", 0 )
        hdu_list["master"].header.set( "alpha", None )
        hdu_list["master"].header.set( "delta", None )

        ##  Write to a FITS file.

        if os.path.isfile( file_name ):
            raise   Exception("%s already exists." % file_name)
        else:
            hdu_list.writeto( file_name )

        self.file_name  = file_name
        self.fits_cube  = fits.open( file_name )

    ##  ========================================================================
    ##  Writing Catalogs

    def write_cat( self, cat_name, file_name ):
        """
        Writes the extension chosen to a formatted ASCII array.

        Arguments:
            cat_name    - name of the extension to get the data array; if the
                          name "master" is given, writes the master array.
            file_name   - file path to write to
        """

        if cat_name.lower() == "master":
            io.write( file_name, self.master )

        else:
            io.write( file_name, self.catalogs[cat_name] )

    ##  ========================================================================
    ##  Additions and Correlation

    def append( self, cat_name, catalog, Rc=None ):
        """
        Append an array to the catalog dictionary.

        Arguments:
            cat_name    - name of the catalog extension
            catalog     - numpy record array of catalog data
            Rc=1        - correlation radius associated to this catalog
                          (semi-arbitrary but kept for dictionary consistancy)
            images      - list of all images associated to this catalog
        """

        ##  Make sure this cat_name is not already in anything important.

        if cat_name in self.catalogs:
            raise   Exception(
                "An %s is already in 'master.catalogs'." % cat_name
            )

        ##  Append catalog to the fits cube.

        hdu     = fits.BinTableHDU.from_columns( catalog )
        hdu.header.set( "EXTNAME",  cat_name )
        hdu.header.set( "Rc",       Rc )
        self.fits_cube.append( hdu )

        ##  Update all class members.

        self.catalogs[ cat_name ]   = catalog
        self.Rc[ cat_name ]         = Rc

    def update( self ):
        """
        Updates the master catalog after any changes have been made.  This
        ensures that all extensions are the same length (filling appended arrays
        with -99 values) and updates the master array with higher resolution
        positions and calculates separation parameters.
        """

        ##  Level all extensions to the size of the master.
        ##      (a) Find the largest extension size.
        ##      (b) Add length to the master and reset ids.
        ##      (c) Add length to each catalog extension.

        ##  Find largest extension size.

        Ns      = []

        for cat in self.catalogs:
            Ns.append( self.catalogs[cat].size )

        self.N  = np.max( Ns )

        ##  Add array of -99s to the master.
        ##  Renumber master ids.

        additional  = np.zeros(self.N-self.master.size, dtype=self.master.dtype)
        additional.fill(-99)
        self.master = np.concatenate( (self.master, additional) )
        self.master["id"]   = np.arange( self.N )

        ##  Add array of -99s to each extension.

        for cat in self.catalogs:

            catalog     = self.catalogs[ cat ]
            additional  = np.zeros( self.N - catalog.size, dtype=catalog.dtype )
            additional.fill(-99)
            catalog                 = np.concatenate( (catalog, additional) )
            catalog["id"]           = np.arange( self.N )
            self.catalogs[ cat ]    = catalog

        ##  Update all master catalog positions with highest resolution data.

        for cat in self.catalogs:

            catalog = self.catalogs[ cat ]

            ##  Choose data with smaller Rc for positions if...
            ##      (a) the master Rc is still -99.
            ##      (b) the master Rc is higher.

            better  = np.where(
                ( catalog["alpha"]    >= 0             ) &
                ( self.master["Rc"]    < 0             ) |
                ( catalog["alpha"]    >= 0             ) &
                ( self.master["Rc"]    > self.Rc[cat]  )
            )[0]

            self.master["alpha"][ better ]  = catalog["alpha"][ better ]
            self.master["delta"][ better ]  = catalog["delta"][ better ]
            self.master["Rc"][ better ]     = self.Rc[ cat ]

        ##  Calculate mean separations.
        ##  Count matches.

        self.master["S"]        = 0
        self.master["matches"]  = 0

        for cat in self.catalogs:

            catalog         = self.catalogs[ cat ]
            matched         = np.where( catalog["alpha"] >= 0 )[0]

            self.master["S"][matched]  += np.sqrt(
                (self.master["alpha"][matched] - catalog["alpha"][matched])**2 +
                (self.master["delta"][matched] - catalog["delta"][matched])**2
            )

            self.master["matches"][matched] += 1

        self.master["S"]       /= (self.master["matches"] - 1)
        self.fits_cube[1].data  = self.master

    def correlate( self, cat_name, catalog, Rc, append=True ):
        """
        Correlates all objects from the new catalog to the existing master
        catalog extension and then adds the created extension to the MCC using
        the Master.append() function.

        Arguments:
            cat_name    - name of the catalog extension to be created
            catalog     - catalog array to correlate to the master
            Rc          - correlation radius (R < Rc is a match)
            append=True - if True, adds non-matched objects to the MCC
        """

        ##  Read in input catalog and add a master id column.

        if "id" not in catalog.dtype.names:
            catalog  = io.add_column( catalog, "id", "int64" )

        ##  Perform correlation with the master catalog.

        M, S, Pa, Nb   = mcc.correlate(
            self.master[ "alpha" ], self.master[ "delta" ],
            catalog[ "alpha" ], catalog[ "delta" ],
            self.master[ "Rc" ], Rc_min=Rc
        )

        ##  Create the new catalog master.
        ##  Append unmatched objects if Append==True.
        new_cat         = np.zeros( self.master.size, dtype=catalog.dtype )
        new_cat.fill(-99)
        new_cat[Pa]     = catalog[ M[Pa] ]

        if append is True:
            new_cat = np.concatenate( (new_cat, catalog[Nb]), axis=0 )

        new_cat["id"]   = np.arange( 1, new_cat.size + 1, dtype="int64" )

        ##  Append the new catalog.
        ##  Update the master catalog and save changes.

        self.append( cat_name, new_cat, Rc=Rc )
        self.update()
        #self.save( overwrite=True )

    def remove_cat( self, cat_name ):

        ##  Remove from fits cube.

        self.fits_cube.pop

        ##  Remove from class members.

        self.catalogs.pop( cat_name )
        self.images.pop( cat_name )
        self.Rc.pop( cat_name )
        self.update()

    ##  ========================================================================

    def set_frames( self, cat_name, fits_list ):
        """
        This function determines, for those objects which have -99 values for
        alpha, whether or not the position of the object is not covered by the
        image data or covered by the data but not present in the original
        catalog.  The column will take on the values
            *   -1          not covered
            *   frame       covered but not detected
        where frame is the photo.image.frame in which the object would be
        present.
        """

        ##  Grab the catalog.
        ##  Add "frame" column if it doesn't already exist.

        catalog = self.catalogs[ cat_name ]

        if "frame" not in catalog.dtype.names:
            catalog = io.add_column( catalog, "frame", "int64", after="id" )

        ##  Create a set of stamp objects for each image.
        ##  Set all 0.0 values to NaN in each image.

        images  = [ photo.image( f ) for f in fits_list ]
        for i in range( len(images) ):
            images[i].data[ np.where(cube[i].data == 0.0) ]   = np.nan

        stamps  = [ photo.stamp( image, S=2, unit="pix" ) for image in images ]

        ##  Find the best frame for all objects in the master catalog.

        catalog["frame"]    = photo.find_best_frame(
            fits_file, self.master["alpha"], self.master["delta"]
        )

        ##  For each frame, look for all objects closest to this frame.

        for i, image in enumerate( cube ):

            io.progress(
                i, len(cube),
                alert="Testing coverage in each frame in %s." % fits_file
            )

            nots    = np.where(
                (catalog["frame"] == image.frame) & (catalog["alpha"] < 0)
            )[0]

            ##  For each object in this frame, target the stamp.

            for n in nots:

                stamps[i].set_target(
                    self.master["alpha"][n], self.master["delta"][n]
                )

                bad = 0
                for k in range( stamps[i].data.shape[0] ):
                    for l in range( stamps[i].data.shape[1] ):
                        if np.isnan( stamps[i].data[k,l] ):
                            bad += 1

                if bad > 2:
                    catalog["frame"][n] = -1

        ##  Save the changes to the master.

        self.catalogs[ cat_name ]   = catalog

        self.save( self.file_name, overwrite=True )
