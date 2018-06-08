"""
This file contains the class object which is the master catalog.
"""

from   .__imports__ import *

##  ============================================================================

##  Master Dtype

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

class Master:

    def __init__( self, file_name, init=False ):
        """
        The Master Catalog Cube (MCC).  The arguments instantiate the object
        from either a file path in which a previous object was written or
        initializes a new MCC.

        Arguments:
            file_name   - file path to an existing MCC
            init=False  - create a new MCC

        Members:
            file_name   - file path to read and write from
            N           - number of objects in the MCC
            master      - the master catalog array (numpy record array)
            cat_list    - list of all catalog extensions
            catalogs    - dictionary of all catalog arrays (numpy record arrays)
            images      - dictionary of an image list per extension
            Rc          = dictionary of correlation radii of input catalogs
        """

        ##  Members

        self.file_name      = file_name
        self.N              = 0
        self.master         = np.zeros( 0, dtype=master_dtype )
        self.cat_list       = []
        self.catalogs       = {}
        self.images         = {}
        self.Rc             = {}

        ##  Initializing file.

        if init is False:
            self.open( file_name )

        else:
            pickle.dump( self, gzip.open(self.file_name, "wb") )

    ##  ========================================================================
    ##  File Management

    def save( self, saveas=None, clobber=False ):
        """
        Saves the MCC object to a python pickle file.

        Arguments:
            saveas=None     - file path to save to; if None, uses existing path
            clobber=False   - if clobber=True, overwrites existing file paths
        """

        ##  Use saveas if provided.

        if saveas is None:
            saveas  = self.file_name

        ##  Don't write over existing file without permission.

        if os.path.isfile( saveas ) and clobber is False:
            raise   Exception( saveas + " already exists." )

        ##  Write self to file.

        pickle.dump( self, gzip.open(saveas, "wb") )

    def open( self, file_name ):
        """
        Opens and retrieves the MCC members from an existing pickle file.

        Arguments:
            file_name       - file path to open
        """

        ##  Open a master file and copy all members.

        MF  = pickle.load( gzip.open(file_name, "rb") )

        self.file_name      = file_name     ##  Don't let this get from the MCC
        self.N              = MF.N          ##  file b/c the file_could could
        self.master         = MF.master     ##  have been changed in terminal.
        self.cat_list       = MF.cat_list
        self.catalogs       = MF.catalogs
        self.images         = MF.images
        self.Rc             = MF.Rc

        del MF

    ##  These are useful if not holding onto all extensions.
    ##  I will probably add these at some point.

    #def get_catalog( self, cat_name ):
    #
    #    MF          = Master_File( self.file_name )
    #    catalog     = MF.catalogs[cat_name]
    #
    #    del MF
    #    return  catalog

    #def update_catalog( self, cat_name, catalog ):
    #
    #    MF                      = Master_File( self.file_name )
    #    MF.catalogs[cat_name]   = catalog
    #    MF.save( clobber=True )
    #
    #    del MF

    ##  ========================================================================
    ##  Writing

    def write( self, cat_name, file_name ):
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

    def write_fits( self, file_name, clobber=False ):
        """
        Write the MCC to a FITS cube.  The zeroth extension is an empty array
        and the miscellaneous member information is written to the header.  The
        first extension is the master catalog array in binary table format.  The
        remaining extensions are the correlated catalog arrays in binary table
        format.  Extensions [1:] may be accessed via their catalong names rather
        than extension index.

        Arguments:
            file_name       - file path to write to
            clobber=False   - if True, overwrites existing file path
        """

        ##  Initialize the FITS object.

        primary_ext     = fits.PrimaryHDU( np.zeros((10,10)) )
        master_ext      = fits.BinTableHDU.from_columns( self.master )
        master_ext.update_ext_name("master")

        hdu_list        = [ primary_ext, master_ext ]

        for i, cat in enumerate( self.cat_list ):

            catalog     = self.catalogs[ cat ]
            extension   = fits.BinTableHDU.from_columns( catalog )
            extension.update_ext_name( cat )
            hdu_list.append( extension )

        hdu_list        = fits.HDUList( hdu_list )

        ##  write info to the fits header

        hdu_list[0].header.set( "FILE_NAME", self.file_name )
        hdu_list[0].header.set( "NUMBER", self.N )
        hdu_list[0].header.set( "ext_1", "Master" )

        for i, cat in enumerate( self.cat_list ):

            hdu_list[0].header.set( "ext_%i" %(i+2), cat )

            N   = np.where( self.catalogs[cat]["id"] >= 0 )[0].size

            hdu_list[cat].header.set( "N", N )
            hdu_list[cat].header.set( "Rc", self.Rc[cat] )

        ##  write to a FITS file

        hdu_list.writeto( file_name, clobber=clobber )

    ##  ========================================================================
    ##  Additions and Correlation

    def append( self, cat_name, catalog, Rc=1, images=None ):
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

        if cat_name in self.cat_list:
            raise   Exception("%s is already in 'Master.cat_list'." % cat_name)

        if cat_name in self.catalogs:
            raise   Exception("%s is already in 'Master.catalogs'." % cat_name)

        ##  Update all parameters.

        self.cat_list.append( cat_name )
        self.catalogs[ cat_name ]   = catalog
        self.images[ cat_name ]     = images
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

        for cat in self.cat_list:

            Ns.append( self.catalogs[cat].size )

        self.N  = np.max( Ns )

        ##  Add array of -99s to the master.
        ##  Renumber master ids.

        additional  = np.zeros(
            self.N - self.master.size, dtype=self.master.dtype
        )
        additional.fill(-99)

        self.master = np.concatenate(
            ( self.master, additional )
        )

        self.master["id"]   = np.arange( 1, self.N + 1 )

        ##  Add array of -99s to each extension.

        for cat in self.cat_list:

            catalog     = self.catalogs[ cat ]

            additional  = np.zeros(
                self.N - catalog.size, dtype=catalog.dtype
            )
            additional.fill(-99)

            catalog         = np.concatenate(
                ( catalog, additional )
            )

            catalog["id"]   = np.arange( 1, self.N + 1 )

            self.catalogs[ cat ]    = catalog

        ##  Update all master catalog positions with highest resolution data.

        for cat in self.cat_list:

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

        for cat in self.cat_list:

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

        self.save( clobber=True )

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

    def add_catalog( self, cat_name, catalog, Rc, append=True, images=None ):
        """
        Correlates all objects from the new catalog to the existing master
        catalog extension and then adds the created extension to the MCC using
        the Master.append() function.

        Arguments:
            cat_name    - name of the catalog extension to be created
            catalog     - catalog array to correlate to the master
            Rc          - correlation radius (R < Rc is a match)
            append=True - if True, adds non-matched objects to the MCC
            images=None - list of all image paths associated to this catalog
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

            new_cat     = np.concatenate( (new_cat, catalog[Nb]), axis=0 )

        new_cat["id"]   = np.arange( 1, new_cat.size + 1, dtype="int64" )

        ##  Append the new catalog.
        ##  Update the master catalog and save changes.

        self.append( cat_name, new_cat, Rc=Rc, images=images )
        self.update()
        self.save( clobber=True )

    ##  ========================================================================

    def test_coverage( self, cat, data_dir=None ):

        ##  Loop through all extensions and for those which are associated with
        ##  a set of images, test for coverage in the field of view in image.

        master      = self.master
        catalog     = self.catalogs[ cat ]
        images      = self.images[ cat ]

        ##  Place the directory in each file name.

        if data_dir is not None:
            for i in range( len(images) ):
                images[i]   = os.path.join( data_dir, images[i] )

        ## Set any unique objects which are not located within an
        ## image equal to -88 for non-detection but covered.

        for im_file in images:

            print( 'Checking object coverage in %s...' % im_file )

            data    = fits.getdata( im_file )
            header  = fits.getheader( im_file )
            world   = WCS( header )

            ## Find pixel coordinates of non_detected unique objects.
            ## Start by assuming all non_dets are out_fields.

            non_dets    = np.where( catalog["alpha"] < 0 )[0]

            ## Determine validity of pixel coordinates.
            ## Criteria:
            ##      1.  Inside of valid pixel ranges.
            ##      2.  Pixel value is not 0.0 or NAN.

            if non_dets.size > 0:

                y, x        = world.wcs_world2pix(
                    master[ non_dets ][ "alpha" ],
                    master[ non_dets ][ "delta" ],
                    1
                )

                y, x        = y.astype('int'), x.astype('int')

                in_pix      = non_dets[
                    np.where(
                        ( x > 0 )               &
                        ( x < data.shape[0] )   &
                        ( y > 0 )               &
                        ( y < data.shape[1] )
                    )[0]
                ]

                if in_pix.size > 0:

                    y, x        = world.wcs_world2pix(
                        master[ in_pix ][ "alpha" ],
                        master[ in_pix ][ "delta" ],
                        1
                    )

                    y, x        = y.astype('int'), x.astype('int')

                    in_fields   = in_pix[
                        np.where(
                            ( data[x,y] != 0.0 )            &
                            ( np.isfinite(data[x,y]) )
                        )[0]
                    ]

                    for i in in_fields:
                        catalog[i].fill( -88 )

        ##  Update the catalog.

        self.catalogs[ cat ]    = catalog
