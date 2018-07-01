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
    3       3.13159         2.71828         Beethoven
"""

from    __future__      import absolute_import
from    __future__      import division
from    __future__      import print_function
from    __future__      import unicode_literals

from    .__imports__    import *

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

def get_configs( configs_file ):
    """
    Returns a dictionary of variables defined in a .cfg file.
    """

    body    = get_body( configs_file )

    configs = {}

    ## Find all variable names.  These are the leftmost value.
    ## All values are the remaining values.
    ## Multi-valued values are designated with ",".

    for i in range( len(body) ):

        variable    = body[i][0]

        multi_val   = False

        for j in range( len(body[i][1:]) ):

            if "," in body[i][j]:

                multi_val   = True

        if multi_val is True:

            value   = " ".join( body[i][1:] )
            value   = value.replace( " ", "" ).split( "," )

        else:

            value   = body[i][1]

        ## Type set values.

        if isinstance( value, list ):

            for j in range( len(value) ):

                if value[j].lower() in ["t","true","f","false"]:

                    value[j]    = bool( value[j] )

                elif value[j].lower() in ["none"]:

                    value[j]    = None

                else:

                    try:

                        value[j]    = float( value[j] )

                        if value[j] % 1 == 0:

                            value[j]    = int( value[j] )

                    except:

                        value[j]    = str( value[j] )

        else:

            if value.lower() in ["t","true","f","false"]:

                value    = bool( value )

            elif value.lower() in ["none"]:

                value    = None

            else:

                try:

                    value    = float( value )

                    if value % 1 == 0:

                        value    = int( value )

                except:

                    value   = str( value )

        ## Finally add the variable and value to the dictionary.

        configs[ variable ] = value

    return configs

##  ========================================================================  ##

def parse_path( full_path ):
    """
    Returns tuple of ( path, name, ext ).  The extension is considered to be
    anything after the first '.' in the file_name.
    """

    path, file_name     = os.path.split( full_path )
    #name, ext           = os.path.splitext( file_name )   ##  the old way

    i, j    = 0, None
    
    while j is None and i < len(file_name):
        if file_name[i] == ".":
            j = i
        else:
            i += 1

    if j is not None:
        name    = file_name[:j]
        ext     = file_name[j:]
    else:
        name    = file_name
        ext     = ""

    return path, name, ext
