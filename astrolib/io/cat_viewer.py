
from astrolib.imports import *
import tkinter as tk
from tkinter import filedialog

##  ============================================================================

def null():
    print( "null" )

##  ============================================================================

class cat_viewer:
    def __init__( self, file_name=None ):

        ##  Catalog members

        self.file_name  = file_name     ##  file name
        self.data       = None          ##  catalog data
        self.dtype      = None          ##  data dtype
        self.cols       = None          ##  list of column names

        ##  GUI members

        window          = None

        main_menu       = None
        file_menu       = None
        edit_menu       = None
        view_menu       = None

        col_frame       = None
        plot_frame      = None

        ##  Initialize GUI.

        self.initialize_gui()

        ##  If a file name was given, open it.

        if file_name is not None:
            self.data   = io.read( self.file_name )
            self.dtype  = self.data.dtype
            self.cols   = self.data.dtype.name

    def initialize_gui( self ):

        ##  Begin.

        self.window     = tk.Tk()
        self.window.title( "Cat Viewer" )

        ##  Menus.

        self.main_menu  = tk.Menu( self.window )
        self.window.config( menu=self.main_menu )

        self.file_menu  = tk.Menu( self.main_menu )
        self.file_menu.add_command( label="Open", command=self.open )
        self.file_menu.add_command( label="Save", command=null )
        self.file_menu.add_command( label="Save As...", command=null )
        self.main_menu.add_cascade( label="File", menu=self.file_menu )

        self.edit_menu  = tk.Menu( self.main_menu )
        self.main_menu.add_cascade( label="Edit", menu=self.edit_menu )

        ##  End.

        self.window.mainloop()

    def open( self ):

        self.file_name  = filedialog.askopenfilename( title="Select file" )
        self.data   = io.read( self.file_name )
        self.dtype  = self.data.dtype
        self.cols   = self.data.dtype.names

##  ============================================================================

if __name__ is "__main__":
    cat_viewer()

