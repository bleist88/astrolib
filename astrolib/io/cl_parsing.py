"""
This file defines the class CL_Parser().  This class manages command line
arguments supplied to a script.  Command line arguments may come in the form of
flagged arguments, i.e...
    script -c configs_file
or through a command, i.e...
    script do
"""

from    __future__      import absolute_import
from    __future__      import division
from    __future__      import print_function
from    __future__      import unicode_literals

from    .__imports__    import *

##  ========================================================================  ##

class CL_Parser:

    def __init__( self, cl_args ):

        self.cl_args    = [ arg for arg in cl_args if ".py" not in arg ]
        self.flags      = {}
        self.commands   = []
        self.parse()

    def parse( self ):

        for i, arg in enumerate( self.cl_args ):

            ##  parse out all flag and key arguments

            if "-" in arg:

                self.flags[ arg ] = self.cl_args[ i + 1 ]

            if "-" not in arg:
                if i > 0 and "-" not in self.cl_args[ i - 1 ]:

                    self.commands.append( arg )

    def get_flag( self, flag, default=None ):

        if flag in self.flags:
            return  self.flags[ flag ]

        else:
            return default

    def get_command( self, command ):

        if command in self.commands:
            return  True
        else:
            return  False

    def help( self ):

        print( "CL_Parser Help:" )
        print()
