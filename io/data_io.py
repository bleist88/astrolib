"""
This file contains functions which are designed to read and write ascii files
to and from numpy record arrays.  The typical text file might look somethin
like:

    ##  This is a comment at the top of the file.
    #<  col_1           int32
    #<  col_2           float32
    #<  col_3           float32
    #<  col_4           U20
    1       3.14159         2.71828         Feynman
    2       2.71828         3.14159         Jefferson
    ##  Here is another comment randomly in the file.
    3       3.13159         2.71828         Beethoven
"""

from    __future__      import absolute_import
from    __future__      import division
from    __future__      import print_function
from    __future__      import unicode_literals

from    .__imports__    import *

##  ========================================================================  ##

def read( file_name, dtype=None ):
    """
    This function reads an ascii file and returns a numpy record array.  If the
    dtype of the ascii data is not specified ( default ), the format of the data
    is specified by a header.  The typical text file might look somethin like:

        ##  This is a comment at the top of the file.
        #<  col_1           int32
        #<  col_2           float32
        #<  col_3           float32
        #<  col_4           U20
        1       3.14159         2.71828         Feynman
        2       2.71828         3.14159         Jefferson
        ##  Here is another comment randomly in the file.
        3       3.13159         2.71828         Beethoven

    Parameters:
        file_name       - str
            name of ascii file
        dtype           - dict
            numpy dtype or numpy like dtype dictionary

    Returns:
        array           - numpy record array
    """

    ## Retrieve body of text and the dtype a text file.

    body, comments, fdtype   = Io.parse_file( file_name )

    if dtype is None:
        dtype   = fdtype

    ## Create an array and fill it with text.

    array       = np.zeros( len(body), dtype=dtype )
    bad_lines   = 0

    for i in range(len( body )):

        ## Write line to array if possible.

        try:
            array[i]    = tuple( body[i] )

        except:
            bad_lines += 1

    ## Inform user to lines that were not written.

    if bad_lines > 0:
        print( "%i lines not read in %s." % ( bad_lines, file_name ) )

    return array

##  ========================================================================  ##

def write(
    file_name, array, header=True, space=3,
    sci=False, ipad=6, fpad=8.6, spad=32,
    keep=False
):
    """
    This function writes an ascii data file from given numpy record array with a
    formatted header written from the dtype of the array.  The file will contain
    a header which looks like:

        #   col_name_1          int32
        #   col_name_2          float32
        #   col_name_3          U27

    Parameters:
        file_name   - str
            name of ascii file
        array       - ndarray
            numpy ndarray to write
        header      - bool
            to write header to the file or not
        space       - int
            number of spaces between columns
        sci         - bool
            hack to use scientific notation for floats
        ipad        - int
            format for integers
        fpad        - float
            format for floats
        spad        - int
            format for strings ( currently pretty lame )
    """

    out_file    = open( file_name, "w" )

    ## Determine line format from array.

    dstring     = Io.get_dstring(
        array.dtype, space=space, sci=sci, ipad=ipad, fpad=fpad, spad=spad
    )

    ## Write header to file.

    if header is True:

        for name in list( array.dtype.names ):

            out_file.write( "#<  " + name )
            out_file.write( (25-len(name)) * " " )
            out_file.write( str(array.dtype[name]) )
            out_file.write( "\n" )

    ## Write formatted lines to file and close.

    for i in range(len( array )):

        out_file.write( dstring % tuple(array[i]) )
        out_file.write( "\n" )

    ##  If keep is True, return the file stream.
    ##  Also return the dstring for consistent writing.
    ##  Otherwise, close the file stream.

    if keep is True:
        out_file.flush()
        return  out_file, dstring
    else:
        out_file.close()

##  ========================================================================  ##

def writeto( out_file, dstring, row_data ):

    out_file.write( dstring % tuple(row_data) )
    out_file.write( "\n" )
    out_file.flush()

##  ========================================================================  ##

def write_configs( file_name, configs, comment=None ):
    """
    Write a configurations file from a configurations dictionary.
    """

    ##  Open file and write comment.

    out_file    = open( file_name, "w" )

    if comment is not None:

        out_file.write( "##  " + comment + "\n\n" )

    else:

        out_file.write( "\n\n" )

    ##  Create value strings from values.

    for key in configs:

        if isinstance( configs[key], (list, tuple) ):

            vals  = []

            for val in configs[key]:

                vals.append( str(val) )

            configs[key]    = ", ".join( vals )

    ##  Write configs to file.

    for key in configs:

        out_file.write( "%-28s  %s\n" % (key, configs[key]) )

    out_file.write("")
    out_file.close()

##  ========================================================================  ##

def add_column( original, col_name, col_format, data=None ):
    """
    This function adds a column to an existing numpy record array and returns
    the result.

    Parameters:
        original        - numpy array
            original numpy record array
        col_name        - str
            column name
        col_format      - str
            column format
        data            - new column array
            data to add

    Returns:
        numpy record array
    """

    new_dtype = { "names":[col_name], "formats":[col_format] }

    for col in original.dtype.names:

        new_dtype["names"].append( col )
        new_dtype["formats"].append( original.dtype[col] )


    new_array = np.zeros( original.size, dtype=new_dtype )

    for col in original.dtype.names:

        new_array[col] = original[col]

    if data is not None:

        new_array[col_name] = data

    return new_array

################################################################################
###   n u m p y   f o r m a t s
#
# DATA_TYPE       DESCRIPTION
#
# S             Byte-String
# U             Unicode Literal
# bool_	        Boolean (True or False) stored as a byte
# int_	        Default integer type (same as C long; normally either int64 or int32)
# intc	        Identical to C int (normally int32 or int64)
# intp	        Integer used for indexing
# int8	        Byte (-128 to 127)
# int16	        Integer (-32768 to 32767)
# int32	            (-2147483648 to 2147483647)
# int64	            (-9223372036854775808 to 9223372036854775807)
# uint8	        Unsigned integer (0 to 255)
# uint16	        (0 to 65535)
# uint32	        (0 to 4294967295)
# uint64	        (0 to 18446744073709551615)
# float_	        Shorthand for float64.
# float16	        Half precision float: sign bit, 5 bits exponent, 10 bits mantissa
# float32	        Single precision float: sign bit, 8 bits exponent, 23 bits mantissa
# float64	        Double precision float: sign bit, 11 bits exponent, 52 bits mantissa
# complex_	    Shorthand for complex128.
# complex64	    Complex number, represented by two 32-bit floats
# complex128	    represented by two 64-bit floats
#
# This table was taken from the scipy.org website.
