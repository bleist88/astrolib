"""
This file defines the class CL_Parser().  This class manages command line
arguments supplied to a script.  Command line arguments may come in the form of
flagged arguments, i.e...
    script -c configs_file
or through a command, i.e...
    script do
"""

from ._imports import *

##  ========================================================================  ##

class cl_parser:

    def __init__( self, cl_args ):

        self.cl_args    = [ arg for arg in cl_args if ".py" not in arg ]
        self.booleans   = {}
        self.flags      = {}
        self.commands   = []

        ##  Parse all arguments.

        for i, arg in enumerate( self.cl_args ):

            ##  Parse out any boolean arguments.

            if "--" in arg:
                self.booleans[ arg ]    = True

            ##  Parse out any flag arguments.

            elif "-" in arg:
                self.flags[ arg ]   = self.cl_args[i + 1]

            ##  Parse out any command arguments.

            else:
                if i > 0:
                    if "--" not in self.cl_args[i - 1]:
                        if "-" not in self.cl_args[i - 1]:
                            self.commands.append( arg )

    def get_boolean( self, bool, default=False ):

        if bool in self.booleans and default == False:
            return  True

        if bool in self.booleans and default == True:
            return  False

        else:
            return  default

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
