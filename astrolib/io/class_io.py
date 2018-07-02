"""
This file contains functions which help to save and open class objects to and
from file.
"""

from .__imports__ import *

##  ============================================================================

def save_obj( obj, saveas, overwrite=False ):
    """
    Writes the instantiation of an object to a python pickle file.

    Arguments:
        obj             - the object to be written to file.
        saveas          - file path to save to; if None, uses existing path
        overwrite=False - if overwrite=True, overwrites existing file paths
    """

    ##  Don't write over existing file without permission.

    if os.path.isfile( saveas ) and overwrite is False:
        raise   Exception( saveas + " already exists.  Set 'overwrite=True'." )

    ##  Write object to file.

    pickle.dump( obj, gzip.open(saveas, "wb") )

##  ============================================================================

def open_obj( obj, file_name, force=False ):
    """
    Retrieves the class attributes from an existing pickle file.

    Arguments:
        obj             - object to write to
        file_name       - file path to open
        force=False     = if force=True, open file even if there are issues
    """

    ##  Open a master file and copy all members.

    instance    = pickle.load( gzip.open(file_name, "rb") )

    ##  Check for discrepencies between object attributes.

    inst_keys   = []
    obj_keys    = []

    for key in instance.__dict__:
        if key not in obj.__dict__:
            inst_keys.append( key )
            print( key + " was present in the file but not the class." )

    for key in obj.__dict__:
        if key not in obj.__dict__:
            obj_keys.append( key )
            print( key + " was present in the class but not the file." )

    if force == False and len(inst_keys) > 0 or len(obj_keys) > 0:

        bad_keys    = "    in file: " + ", ".join(inst_keys) + "\n"
        bad_keys   += "    in obj:  " + ", ".join(obj_keys)

        raise   Exception("There were attribute discrepencies between objects.")

    ##  Copy members from the opened object.

    for key in instance.__dict__:
        obj.__dict__[ key ] = instance.__dict__[ key ]
