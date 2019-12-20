#!/usr/bin/python3

## @package gencfs 
# @author urs lindegger urs@linurs.org  

## @todo 
# - 

## @mainpage gencfs
# gencfs is a simple gui for encfs
# 

import os
import subprocess
import shlex
import shutil
import argparse
import logging
import sys

try:
   import pexpect
## indicates that pexpect is available
   expect=True 
except:
   expect=False
   
from tkinter import *   
from tkinter import messagebox   
from tkinter import filedialog    

## Version of gencfs
gencfsversion="0.7"

## favicon file to seen in window decoration
faviconname='favicon.gif'

buttonwidth=20

class app_t():
##
# The constructor for the GUI application   
    def __init__(self):
        userpath=os.path.expanduser("~")           # check what user
        configdir=userpath+"/.GEncFs"
        if os.access(configdir, os.F_OK)==False:  # check if user has a directory containing persistent data
          os.mkdir(configdir)                                    # if not create the directory
        configfile="conf"
        ## path to config file         
        self.pathtoconfig=configdir+"/"+configfile
        logging.debug("Config file "+self.pathtoconfig)
        if os.access(self.pathtoconfig, os.F_OK)==False:   # check if file exists containing persistent data
          os.system("touch "+self.pathtoconfig)               # if not create the empty file
        pathtoconfigfile=open(self.pathtoconfig) # now read the file containing persistent data or being empty
        pathstoencfs=pathtoconfigfile.readlines()  
        pathtoconfigfile.close()
        
        ## the list box does not point to anything the last position is taken
        self.index='0'
        
        ## setup the gui stuff
        self.window=Tk()
        self.window.title('Gui for EncFs')
        
        # add an icon
        img = PhotoImage(file=favicon)
        self.window.call("wm", "iconphoto", self.window, "-default", img)
        self.window.resizable(width=FALSE, height=FALSE)
        
        ## create the menus   
        self.menubar = Menu(self.window)
        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Add directory for .crypt and crypt", command=self.add)
        filemenu.add_command(label="Remove directory from list", command=self.remove)
        filemenu.add_command(label="Create .crypt and crypt", command=self.create)
        filemenu.add_separator()
        filemenu.add_command(label="Change Password", command=self.passwd)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)
        self.menubar.add_command(label="About", command=self.about)
        self.window.config(menu=self.menubar)
        
        # add the password label and entry field
        self.window.label=Label(self.window, text='Password')
        self.window.label.grid(row=1)
        self.window.password=Entry(self.window, show='*')
        self.window.password.grid(row=2)
        
        # add the path label and value
        self.window.labelpath=Label(self.window, text='Path to the .crypt and crypt directories')
        self.window.labelpath.grid(row=3)
        self.dir_gui=StringVar()
        self.window.pathlabel = Label(master=self.window, textvariable=self.dir_gui)
        self.window.pathlabel.grid(row=4)
        
        self.mounted_gui=StringVar()
        self.window.mountedlabel = Label(master=self.window, textvariable=self.mounted_gui)
        self.window.mountedlabel.grid(row=5)

        # set up and register the buttons
        self.window.mountbutton=Button(master=self.window,text='Mount EncFs',width=buttonwidth, command=self.encfsmount)
        self.window.mountbutton.grid(row=6)
        self.window.umountbutton=Button(master=self.window,text='Umount EncFs',width=buttonwidth, command=self.encfsumount)
        self.window.umountbutton.grid(row=7)
        self.window.openbutton=Button(master=self.window,text='Open EncFs',width=buttonwidth, command=self.encfsopen)
        self.window.openbutton.grid(row=8)
        
        # set up the listbox and its label
        self.window.listbox = Listbox(self.window,  width=50,  height=5,  justify='center')
        self.window.listbox.bind('<<ListboxSelect>>', self.listboxchange)
        self.window.listbox.grid(row=9)
        for item in pathstoencfs:
          i=item.strip()  
          if len(i)>0:  
            self.window.listbox.insert(END, i)
        self.window.listbox.select_set(0)  # selects the first one, so something is selected    
        self.dir_gui.set(self.window.listbox.get(0))
        self.pathtoencfs=self.window.listbox.get(0)
        self.update_gui()
        
##
# runs the gui
    def run(self):
        self.window.mainloop()        

##
#
    def is_mounted(self):
        return os.path.ismount(self.pathtoencfs+"/crypt")
        
    def update_gui(self):
        if self.is_mounted()==True:
            self.mounted_gui.set("Mounted")
            self.window.mountbutton.config(relief=SUNKEN)
            self.window.umountbutton.config(relief=RAISED)
            self.window.openbutton.config(relief=RAISED)
        else:
            self.mounted_gui.set("Not Mounted")
            self.window.mountbutton.config(relief=RAISED)
            self.window.umountbutton.config(relief=SUNKEN)
            self.window.openbutton.config(relief=SUNKEN)
        
##
# listbox has changed
    def listboxchange(self, evt):
       w = evt.widget
       try:
         index = int(w.curselection()[0])
       except:
            logger.debug("listboxchange exception")
            logger.debug(w.curselection())
            index=0
       self.dir_gui.set(self.window.listbox.get(index))
       self.pathtoencfs=self.window.listbox.get(index)
       self.update_gui()
  
##
# Quits the application
    def quit(self):
           self.window.destroy()

##
# updates the config file by re-creating it
    def updateconfig(self):
        items=self.window.listbox.get(0, END)
        pathtoconfigfile=open(self.pathtoconfig,  'w') # now write the file containing persistent data
        for i in items:
            pathtoconfigfile.write(i+"\n")  
        pathtoconfigfile.close()

##
# Check if directory exists alerady
    def existconfig(self, n):
        items=self.window.listbox.get(0, END)
        value=False
        for i in items:
            if i==n:
                value=True
        return value        

##
# Adds new directory to the list
    def add(self):
        dname = filedialog.askdirectory(initialdir='~')   
        if self.existconfig(dname)==True:
                  messagebox.showinfo("Info","Directory "+dname+" already exists in the list")       
        else:
            if os.path.isdir(dname)==False:
                messagebox.showinfo("Info","Directory "+dname+" does not exist and will be created")       
                os.mkdir(dname)
            self.window.listbox.insert(END, dname)
            self.updateconfig()  
##
# Removes directory from the list
    def remove(self):
        self.window.listbox.delete(ANCHOR)
        self.updateconfig()

##
# Shows abbout messagebox
    def about(self):
         messagebox.showinfo("About","Gencfs a gui front end for Encfs from https://www.linurs.org \nVersion "+gencfsversion)       

##
# Mounts the encripted directory
    def encfsumount(self):
         cmd ="fusermount -u "+self.pathtoencfs+"/crypt"
         logger.debug(cmd)
         args=shlex.split(cmd)
         p = subprocess.Popen(args, 
                              stdin=subprocess.PIPE, 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, # standard err are passed to stdout
                              ) # open new process
         stdout_value, stderr_value = p.communicate()# communicate is a one time action, afterwards p is closed
         if (stdout_value==b''):
          messagebox.showinfo("umount","Successfully umounted")
         else:  
          messagebox.showinfo("umount",stdout_value)
         self.update_gui()

##
# Un-mounts the encripted directory           
    def encfsmount(self):
         if self.is_mounted()==False:
             password=self.window.password.get()
             b=password.encode('utf-8')
             cmd ="encfs --stdinpass "+self.pathtoencfs+"/.crypt "+self.pathtoencfs+"/crypt" # call encfs without promting for password
             logger.debug(cmd)
             args=shlex.split(cmd)
             
             p = subprocess.Popen(args,  
                                  stdin=subprocess.PIPE, 
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, # standard err are passed to stdout
                                  ) # open new process
            
             stdout_value, stderr_value = p.communicate(b) # communicate is a one time action, afterwards p is closed
             if (stdout_value==b''):
              messagebox.showinfo("mount","Successfully mounted")
             else: 
              messagebox.showinfo("mount",stdout_value)
             self.update_gui()   
         else:
             messagebox.showinfo("mount",self.pathtoencfs+"/crypt is already mounted")

##
# opens the encripted directory           
    def encfsopen(self):
         if self.is_mounted()==True:
            cmd="xdg-open "+self.pathtoencfs+"/crypt"
            os.system(cmd)

##
# creates .crypt and crypt directories
    def create(self):
         if os.path.isdir(self.pathtoencfs)==False:
               messagebox.showinfo("Error","Directory "+self.pathtoencfs+" not found")
         else:      
             ## path to encripted directory
             self.dcrypt=self.pathtoencfs+"/.crypt"
             ## mounting point for encripted directory (decrypted directory)
             self.crypt=self.pathtoencfs+"/crypt"
             if os.path.isdir(self.crypt)==False:
                    messagebox.showinfo("Info","Mounting point "+self.crypt+" will be created")       
                    os.mkdir(self.crypt) 
             if os.path.isdir(self.dcrypt)==True:
                    messagebox.showinfo("Info","Crypted directory "+self.dcrypt+" already exist")
                    if len(os.listdir(self.dcrypt))>0:
                        messagebox.showinfo("Error","Crypted directory is not empty")             
                    else:
                        ## indication if new password has to be entered or existing password has to be changed
                        self.changepassword=False
                        self.newpassword()        
             else:
                    messagebox.showinfo("Info","Crypted directory "+self.dcrypt+" will be created")       
                    os.mkdir(self.dcrypt) 
                    self.changepassword=False
                    self.newpassword()          

##
# destroys the password window and re-shows the main window
    def destroypasswordwindow(self):
            self.window.deiconify()
            self.newpasswordwindow.destroy()

##
# creates the password window that is used to enter a password for newly created directories but also to change the password for existing directories.
    def newpassword(self):
        if (expect==True) or (self.changepassword==False):
            self.window.withdraw()
            
            ## window to set the password      
            self.newpasswordwindow=Toplevel()
            self.newpasswordwindow.protocol("WM_DELETE_WINDOW", self.destroypasswordwindow)
            self.newpasswordwindow.title('Password')
            
            ## show what dir is selected
            self.window.dirtext=Label(self.newpasswordwindow, text='Selected directory', width=20,  anchor=W)
            self.window.dirtext.grid(column=0,  row=0, sticky= W)
            self.window.dirvalue=Label(self.newpasswordwindow, text=self.dcrypt, width=40,  anchor=W)
            self.window.dirvalue.grid(column=1,  row=0, sticky= W)
            
            ## setup password entry variable
            self.newpassword1=StringVar()
            self.window.passlabel1=Label(self.newpasswordwindow, text='New Password', width=20,  anchor=W)
            self.window.passlabel1.grid(column=0,  row=1, sticky= W)
            ## setup password entry        
            self.pass1=Entry(master=self.newpasswordwindow,
                                       textvariable=self.newpassword1, show='*',     width=40 )
            self.pass1.grid(column=1,  row=1)
            
            ## setup password entry variable for confirmation
            self.newpassword2=StringVar()
            self.window.passlabel2=Label(self.newpasswordwindow, text='Verify Password', width=20,  anchor=W)
            self.window.passlabel2.grid(column=0,  row=2, sticky= W)
            ## setup password entry for confirmation
            self.pass2=Entry(master=self.newpasswordwindow,
                                       textvariable=self.newpassword2, show='*',     width=40 )
            self.pass2.grid(column=1,  row=2)
    
           ## setup the ok button
            self.okbutton=Button(master=self.newpasswordwindow,
                                              text='OK',
                                              width=20, 
                                              command=self.okpassword)
            self.okbutton.grid(column=1,
                                         row=3,
                                         sticky=W)
           ## setup the cancel button
            self.cancelbutton=Button(master=self.newpasswordwindow,
                                              text='CANCEL',
                                              width=20, 
                                              command=self.cancelpassword)
            self.cancelbutton.grid(column=0,
                                             row=3,
                                             sticky=W)
        elif (expect==False):
                 messagebox.showinfo("Error","pexpect needs to be installed for the password change. Install it. See: https://pexpect.readthedocs.io \n")                                      
##
# Ok button pressed in password window
    def okpassword(self):
        self.newpasswordwindow.destroy()
        p1=self.newpassword1.get()+'\n'
        p2=self.newpassword2.get()+'\n'
        newb=p1.encode('utf-8')
        if(p1 != p2):
             messagebox.showinfo("Error","Passwords do not match")       
        elif self.changepassword==False:  # create new directory
            cmd ="encfs --stdinpass --standard "+self.dcrypt+" "+self.crypt # call encfs to create and mount the crypted directory
            logger.debug(cmd)
            
            args=shlex.split(cmd)
            p = subprocess.Popen(args,  
                              stdin=subprocess.PIPE, 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, # standard err are passed to stdout
                              ) # open new process
           
            stdout_value, stderr_value = p.communicate(newb) # communicate is a one time action, afterwards p is closed
            if len(os.listdir(self.dcrypt))<=0:
                    messagebox.showinfo("Error","Failed to create\n"+stdout_value.decode("utf-8") )       
        else:   # change password on existing directory       
                 # make sure it is unmounted 
                 cmd ="fusermount -u "+self.crypt
                 logger.debug(cmd)
                 args=shlex.split(cmd)
                 p = subprocess.Popen(args, 
                                      stdin=subprocess.PIPE, 
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, # standard err are passed to stdout
                                      ) # open new process
                 stdout_value, stderr_value = p.communicate()# communicate is a one time action, afterwards p is closed 
           
                 # change the password using pexpect 
                 password=self.window.password.get()
                 b=password.encode('utf-8')
                 cmd="encfsctl passwd "+self.dcrypt
                 logger.debug(cmd)
                 child = pexpect.spawn(cmd)
                 try:
                    child.expect("EncFS Password:", timeout=2)
                 except:
                       messagebox.showinfo("Error",str(child))
                 child.sendline(b)             
                 
                 try:
                    child.expect("New Encfs Password:", timeout=2)
                 except:
                    pass
                 
                 if child.terminated==False:
                     child.sendline(p1)
                     try:
                            child.expect("Verify Encfs Password:", timeout=2)
                     except:
                           messagebox.showinfo("Error",str(child))    
                     child.sendline(p2)
                 
                     try:
                            child.expect("Volume Key successfully updated.", timeout=10)
                     except:
                           messagebox.showinfo("Error",str(child))    
                 after=child.after
                 messagebox.showinfo("Info",after.decode("utf-8"))   
        self.window.deiconify()            
                         
##
# Cancel button pressed in password window
    def cancelpassword(self):
        self.newpasswordwindow.destroy()
        self.window.deiconify()

##
# change the password of an existing directory
    def passwd(self):
         self.dcrypt=self.pathtoencfs+"/.crypt"
         self.crypt=self.pathtoencfs+"/crypt"
 
         self.changepassword=True
         self.newpassword()       

if __name__ == "__main__":
      ## manage the command line parameters
    # sets default values to variables and modifies their content according the command line parameter passed
    # additionally it handles the -h and --help command line parameter automatically
    parser = argparse.ArgumentParser(
                                     description='gencfs - A gui for encfs', 
                                     epilog='urs@linurs.org')
    ## command line option to show the programs version
    parser.add_argument('-v', '--version', action='version', \
    ## version used in command line option to show the programs version
    version='%(prog)s '+gencfsversion)
    ## command line option to enable debug messages
    parser.add_argument('-d', '--debug',   help="print debug messages",   action='store_true')  

    ## the command line arguments passed
    args = parser.parse_args()      
    
    # Configuring the logger. Levels are DEBUG, INFO, WARNING, ERROR and CRITICAL
    # the parameter filename='example.log' would write it into a file
    logging.basicConfig() # init logging 
    ## The root logger 
    logger = logging.getLogger() 
    if args.debug==True:
        logger.setLevel(logging.DEBUG)    # the level producing debug messagesl
    else:    
        logger.setLevel(logging.WARNING)
    logger.debug('Logging debug messages')
    
    # stuff to be logged before the logger came alive
    if expect==False:
         logger.debug('Packet pexpectl not found')
    
    if shutil.which("encfs")==None:
         logger.error('encfs not found')
        
    ## pyinstaller stuff required to create bundled versions:      
    frozen = 'not '
    if getattr(sys, 'frozen', False): # pyinstaller adds the name frozen to sys 
            frozen = ''  # we are running in a bundle (frozen)
            ## temporary folder of pyinstaller
            bundle_dir = sys._MEIPASS  
    else:
            bundle_dir = os.path.dirname(os.path.abspath(__file__))   # we are running in a normal Python environment 
   
    logging.debug('Script is '+frozen+'frozen')
    logging.debug('Bundle dir is '+bundle_dir )
    logging.debug('sys.argv[0] is '+sys.argv[0] )
    logging.debug('sys.executable is '+sys.executable )
    logging.debug('os.getcwd is '+os.getcwd() )

## makes that the files are found
    favicon=bundle_dir+os.sep+faviconname    
    if (os. path. isfile(favicon)==False):
        logging.debug(favicon+' not found' )
        favicon="/usr/share/gencfs/"+faviconname
        logging.debug('so try to find it at '+favicon )
        if (os. path. isfile(favicon)==False):
             logging.error(faviconname+' not found')
             exit()
        
## start the application    
    app=app_t()
    app.run()
