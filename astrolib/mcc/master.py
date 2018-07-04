"""
This file houses the managers used to manage the field, data, filters and SEDs.
"""

from .__imports__   import *

##  ============================================================================

##  Define the master catalog dtype.

master_dtype    = {
    "names":    [
        "id",  "matches", "alpha", "delta", "Rc", "S", "n", "Rn"
    ],
    "formats":  [
        "int64", "int64", "float64", "float64", "float64", "float64",
        "int64", "float64"
    ]
}

##  ============================================================================

class master:

    def __init__( self, file_name, init=False ):

        ##  Members

        self.file_name      = file_name

        self.alpha0         = None
        self.detla0         = None

        self.master         = np.zeros(0, dtype=master_dtype)
        self.N              = None

        self.list           = []
        self.images         = {}
        self.catalogs       = {}
        self.Rc             = {}

        ##  Initialization

        if init is False:
            self.open( file_name )

        else:
            pickle.dump( self, gzip.open(self.file_name, "wb") )

    def display( self ):
        """
        Display attributes into the terminal.
        """
        print(  "Master:  ",        self.file_name      )
        print(  "Number:  ",        self.N              )
        print(  "alpha0:  ",        self.alpha0         )
        print(  "delta0:  ",        self.delta0         )
        print(                                          )
        print(  "extensions:  ",    len(self.list)      )
        print(  "   0:    ",        "master"            )
        for i, ext in enumerate( self.list ):
            print(  "  ", i+1, ":  ",     ext           )
        print(                                          )

##  ========================================================================
    ##  File Management

    def save( self, saveas=None, overwrite=False ):
        """
        Saves the object to a python pickle file.

        Arguments:
            saveas=None     - file path to save to; if None, uses existing path
            overwrite=False - if overwrite=True, overwrites existing file paths
        """

        if saveas is None:
            saveas  = self.file_name

        io.save_obj( self, saveas, overwrite=overwrite )

    def open( self, file_name, force=False ):
        """
        Opens and retrieves the class attributes from an existing pickle file.

        Arguments:
            file_name       - file path to open
        """

        io.open_obj( self, file_name, force=force )

    ##  ========================================================================
    ##  Writing Catalogs

    def write_cat( self, cat_name, file_name ):
        """
        Writes the extension chosen to a formatted ASCII array.

        Arguments:
            cat_name    - name of the extension to get the data array; if the
                          name 'master' is given, writes the master array.
            file_name   - file path to write to
        """

        if cat_name.lower() == "master":
            io.write( file_name, self.master )

        else:
            io.write( file_name, self.catalogs[cat_name] )

    def write_fits( self, file_name, overwrite=False ):
        """
        Write the MCC to a FITS cube.  The zeroth extension is an empty array
        and the miscellaneous member information is written to the header.  The
        first extension is the master catalog array in binary table format.  The
        remaining extensions are the correlated catalog arrays in binary table
        format.  Extensions [1:] may be accessed via their catalong names rather
        than extension index.

        Arguments:
            file_name       - file path to write to
            overwrite=False - if True, overwrites existing file path
        """

        ##  Initialize the FITS object.

        primary_ext     = fits.PrimaryHDU( np.zeros((10,10)) )
        master_ext      = fits.BinTableHDU.from_columns( self.master )
        master_ext.header["EXTNAME"]    = "master"

        hdu_list        = [primary_ext, master_ext]

        for i, cat in enumerate( self.list ):

            catalog     = self.catalogs[ cat ]
            extension   = fits.BinTableHDU.from_columns( catalog )
            extension.header["EXTNAME"] = cat
            hdu_list.append( extension )

        hdu_list        = fits.HDUList( hdu_list )

        ##  Write info to the fits header.

        hdu_list[0].header.set( "FILE_NAME", self.file_name )
        hdu_list[0].header.set( "NUMBER", self.N )
        hdu_list[0].header.set( "ext_1", "Master" )

        for i, cat in enumerate( self.list ):

            hdu_list[0].header.set( "ext_%i" %(i+2), cat )

            N   = np.where( self.catalogs[cat]["id"] >= 0 )[0].size

            hdu_list[cat].header.set( "N", N )
            hdu_list[cat].header.set( "Rc", self.Rc[cat] )

        ##  Write to a FITS file.

        hdu_list.writeto( file_name, overwrite=overwrite )

    ##  ========================================================================
    ##  Additions and Correlation

    def append( self, cat_name, catalog, Rc=1, IM=None ):
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

        if cat_name in self.list:
            raise   Exception("An %s is already in 'Master.list'." % cat_name)

        if cat_name in self.catalogs:
            raise   Exception("An %s is already in 'Master.catalogs'." % cat_name)

        ##  Update all parameters.

        self.list.append( cat_name )
        self.catalogs[ cat_name ]   = catalog
        self.images[ cat_name ]     = IM
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

        for cat in self.list:

            Ns.append( self.catalogs[cat].size )

        self.N  = np.max( Ns )

        ##  Add array of -99s to the master.
        ##  Renumber master ids.

        additional  = np.zeros(self.N-self.master.size, dtype=self.master.dtype)
        additional.fill(-99)
        self.master = np.concatenate( (self.master, additional) )
        self.master["id"]   = np.arange( 1, self.N + 1 )

        ##  Add array of -99s to each extension.

        for cat in self.list:

            catalog     = self.catalogs[ cat ]
            additional  = np.zeros( self.N - catalog.size, dtype=catalog.dtype )
            additional.fill(-99)
            catalog                 = np.concatenate( (catalog, additional) )
            catalog["id"]           = np.arange( 1, self.N + 1 )
            self.catalogs[ cat ]    = catalog

        ##  Update all master catalog positions with highest resolution data.

        for cat in self.list:

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

        for cat in self.list:

            catalog         = self.catalogs[ cat ]
            matched         = np.where( catalog["alpha"] >= 0 )[0]

            self.master["S"][matched]  += np.sqrt(
                (self.master["alpha"][matched] - catalog["alpha"][matched])**2 +
                (self.master["delta"][matched] - catalog["delta"][matched])**2
            )

            matched = np.where( catalog["alpha"] >= 0 )[0]
            self.master["matches"][matched] += 1

        self.master["S"]   /= (self.master["matches"] - 1)

        ##  Save.

        self.save( overwrite=True )

    def find_neighbors( self ):
        """
        For all objects in the master catalog, find the nearest neighbor and
        the radial distance (sit back, this may take a while).
        """

        master  = self.master

        for i in range( master.size ):

            io.progress( i, master.size )

            other   = np.where( master["id"] != master[i]["id"] )[0]

            R       = np.sqrt(
                (master[i]["alpha"] - master[other]["alpha"])**2 +
                (master[i]["delta"] - master[other]["delta"])**2
            )

            r       = np.min( R )

            j       = other[ np.where( R == r )[0] ][0]

            master[i]["n"]  = master[j]["id"]
            master[i]["Rn"] = np.sqrt(
                (master[i]["alpha"] - master[j]["alpha"])**2 +
                (master[i]["delta"] - master[j]["delta"])**2
            )

    def add_catalog( self, cat_name, catalog, Rc, append=True, IM=None ):
        """
        Correlates all objects from the new catalog to the existing master
        catalog extension and then adds the created extension to the MCC using
        the Master.append() function.

        Arguments:
            cat_name    - name of the catalog extension to be created
            catalog     - catalog array to correlate to the master
            Rc          - correlation radius (R < Rc is a match)
            append=True - if True, adds non-matched objects to the MCC
            IM=None     - image manager for the input catalog (if applicable)
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
        self.save( overwrite=True )

    ##  ========================================================================
    ##  This routine is currently down.  I have this written with images as
    ##  file paths rather than image managers.

    # def test_coverage( self, cat, data_dir=None ):
    #
    #     ##  Loop through all extensions and for those which are associated with
    #     ##  a set of images, test for coverage in the field of view in image.
    #
    #     master      = self.master
    #     catalog     = self.catalogs[ cat ]
    #     images      = self.images[ cat ]
    #
    #     ##  Place the directory in each file name.
    #
    #     if data_dir is not None:
    #         for i in range( len(images) ):
    #             images[i]   = os.path.join( data_dir, images[i] )
    #
    #     ## Set any unique objects which are not located within an
    #     ## image equal to -88 for non-detection but covered.
    #
    #     for im_file in images:
    #
    #         print( 'Checking object coverage in %s...' % im_file )
    #
    #         data    = fits.getdata( im_file )
    #         header  = fits.getheader( im_file )
    #         world   = WCS( header )
    #
    #         ## Find pixel coordinates of non_detected unique objects.
    #         ## Start by assuming all non_dets are out_fields.
    #
    #         non_dets    = np.where( catalog["alpha"] < 0 )[0]
    #
    #         ## Determine validity of pixel coordinates.
    #         ## Criteria:
    #         ##      1.  Inside of valid pixel ranges.
    #         ##      2.  Pixel value is not 0.0 or NAN.
    #
    #         if non_dets.size > 0:
    #
    #             y, x        = world.wcs_world2pix(
    #                 master[ non_dets ][ "alpha" ],
    #                 master[ non_dets ][ "delta" ],
    #                 1
    #             )
    #
    #             y, x        = y.astype('int'), x.astype('int')
    #
    #             in_pix      = non_dets[
    #                 np.where(
    #                     ( x > 0 )               &
    #                     ( x < data.shape[0] )   &
    #                     ( y > 0 )               &
    #                     ( y < data.shape[1] )
    #                 )[0]
    #             ]
    #
    #             if in_pix.size > 0:
    #
    #                 y, x        = world.wcs_world2pix(
    #                     master[ in_pix ][ "alpha" ],
    #                     master[ in_pix ][ "delta" ],
    #                     1
    #                 )
    #
    #                 y, x        = y.astype('int'), x.astype('int')
    #
    #                 in_fields   = in_pix[
    #                     np.where(
    #                         ( data[x,y] != 0.0 )            &
    #                         ( np.isfinite(data[x,y]) )
    #                     )[0]
    #                 ]
    #
    #                 for i in in_fields:
    #                     catalog[i].fill( -88 )
    #
    #     ##  Update the catalog.
    #
    #     self.catalogs[ cat ]    = catalog
