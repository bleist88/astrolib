#   Io

##  Reading and Writing Arrays

The primary functions in the Io package are the Io.read() and Io.write()
functions which read in formatted ASCII files to numpy record arrays as well as
write those arrays to ASCII files with a formatted header.  A typical file that
these would read and write to would look something like this.

```ascii
##  Example of an array in ASCII form.
#<  ID                  int64
##  name                U12                     ##  this is just a comment
#<  tau                 float64                 ##  tau is better than pi
#<  alpha               float64
#<  delta               float64
    1   particle    6.2831853   150.232112  2.32451123      ##  comments can be
    2   star        6.2831853   151.958392  1.68382912      ##  placed anywhere
    3   galaxy      6.2831853   150.291095  3.48573929
    4   cluster     6.2831853   149.291095  2.42573929
```

The column formats are specified lines which start with `#<`.  The name of the
column comes next and is followed by the column format.  At present, these
arrays are limited to floats, integers and strings.  All of the following are
acceptable to use as specifiers.

    *   int32       32 bit integer
    *   i4          32 bit integer
    *   int64       64 bit integer
    *   i8          64 bit integer
    *   float32     32 bit float
    *   f4          32 bit float
    *   float64     64 bit float
    *   f8          64 bit float
    *   U#          string of length #
    *   S#          bit string of length #

Comments are specified by `##` and everything after will not be read in.  These
may freely be placed anywhere in the body of the file.  As comments are
completely ignored by the `Io.read()` function, there is no way for them to be
written back on to an ASCII file if the arrays are written later.  Spaces are
also free to exist in the file and are simply ignored.

Enough talk, more do!

```python

import numpy as np
import Io

##  Assume that a file similar to the one shown above exists in this directory.
##  Read in that file and play with the array.

data    = Io.read( "file_above_name.dat" )

radius  = np.sqrt( data["alpha"]**2 + data["delta"]**2 )

if data[0]["tau"] > np.pi:
    print( "Well this is certainly going to print, isn't it?" )
    print( "Yes it will, my friend.  Yes it will." )

##  Now what if that file had not had a format header at the top of it?!
##  One can create a dtype dictionary just as one would do for a numpy record
##  array.

data_dtype  = {
    "names":    [ "ID", "name", "tau", "alpha", "delta" ],
    "formats":  [ "i8", "U12",  "f8", "f8", "f8" ]
}
data        = Io.read( "file_above_name.dat", dtype=data_dtype )

##  One can also get dtypes from other files just by searching for a header.
##  This is nice if you only want to write one header at the top of a file.
##  Then you can simply rewrite all of the other files and they'll get a header.

data_dtype  = Io.get_dtype( "file_above_name.dat" )
other       = Io.read( "another_file_name.dat", dtype=data_dtype )

##  Now one can take any numpy record array and write it to a file.
##  The extension is completely free to the user to choose.

Io.write( "out_file.dat", other )
```
