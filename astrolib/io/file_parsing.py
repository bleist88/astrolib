"""
This file contains the functions which deal with parsing a text file for the
body, comments, and dtype.  The typical text file might look something like:

    ##  This is a comment at the top of the file.
    #<  col_1           int32
    #<  col_2           float32
    #<  col_3           float32
    #<  col_4           U20
    1       3.14159         2.71828         Feynman
    2       2.71828         3.14159         Jefferson
    ##  Here is another comment randomly in the file.
    3       3.14159         2.71828         Beethoven
"""

from ._imports import *

##  ========================================================================  ##

def parse_file( file_name ):
    """
    This function parses an ascii file for the body, comments, and dtype.

    Returns:
        body        - list
            This is a 2-D list of split text.
        comments    - list
            This is a 1-D list of all comments found within the file.
        dtype       - dictionary
            This is a numpy like dtype dictionary.

    Parameters:
        file_name   - str
            This is the path to the ascii file to read.
    """

    text        = open( file_name, "r" ).readlines()

    body        = []
    comments    = []
    dtype       = { "names": [], "formats": [] }

    ## Loop through all lines of the file and append text and comments
    ## appropriately.

    for i in range( len(text) ):

        line    = text[i].split()

        if len( line ) > 0:

            if line[0] == "#<":

                dtype["names"].append( line[1] )
                dtype["formats"].append( line[2] )

            elif line[0][0] == "#":

                comments.append( text[i].replace("\n","") )

            else:

                ## Check for comments hidden in the line.

                hidden_comment, j  = False, 0

                while hidden_comment is False and j < len( line ):

                    if "#" in line[j]:
                        hidden_comment  = True
                    else:
                        j   += 1

                ## Append to comments and body appropriately.

                if hidden_comment is True:

                    comments.append( line[j:] )
                    body.append( line[:j] )

                else:

                    body.append( line )

    ## Set the dtype to None if it has no length.

    if len( dtype["names"] ) == 0:

        dtype = None

    ## Return all.

    return body, comments, dtype

def get_body( file_name ):
    """
    This function uses parse_file() to retrieve the body from a file.
    """

    return parse_file( file_name )[0]

def get_comments( file_name ):
    """
    This function uses parse_file() to retrieve the comments from a file.
    """

    return parse_file( file_name )[1]

def get_dtype( file_name ):
    """
    This function uses parse_file() to retrieve the dtype from a file.
    """

    return parse_file( file_name )[2]

##  ========================================================================  ##

def parse_path( full_path ):
    """
    Returns tuple of ( path, name, ext ).  The extension is considered to be
    anything after the first '.' in the file_name.
    """

    path, file_name     = os.path.split( full_path )
    name, ext           = os.path.splitext( file_name )   ##  the old way

    ##  An alternate way to find name, ext.
    ##
    # i, j    = 0, None
    #
    # while j is None and i < len(file_name):
    #     if file_name[i] == ".":
    #         j = i
    #     else:
    #         i += 1
    #
    # if j is not None:
    #     name    = file_name[:j]
    #     ext     = file_name[j:]
    # else:
    #     name    = file_name
    #     ext     = ""

    return path, name, ext
