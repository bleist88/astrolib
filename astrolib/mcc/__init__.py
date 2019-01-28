"""
A Master Catalog Correlation Package.
"""

from    .master         import master
from    .create         import create
from    .correlation    import correlate, clean_duplicates, combine
from    .stamp          import stamp

##  The old master and create modules.  These used object saves rather than the
##  the FITS file that is used now.
#from    ._old_master    import master   as master_obj
#from    ._old_create    import create   as create_obj

