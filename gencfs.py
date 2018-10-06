#!/usr/bin/python3

## @package gencfs 
# @author urs lindegger urs@linurs.org  

## @todo 
# - license
# - pyinstaller version
# - check if mounted before mounting cat /proc/mounts
# - use tab insted of new window or withdraw() Removes the window from the screen (without destroying it). To redraw the window, use deiconify. 
#       When the window has been withdrawn, the state method returns “withdrawn”. Top window can be more than once 
# - use event handlers 
# - doxygen
# - block top window when child windows are open
# - support checkfiles other than .encfs6.xml or just to see if files are there
# - add verion number
# - 0o777 is ok?
# - why to read from stderr
#

## @mainpage gencfs
# gencfs is a simple gui for encfs
# 

import os
import subprocess
import shlex
import argparse
import logging
import sys

try:
   import pexpect
   expect=True
except:
   expect=False
   
from tkinter import *   
#from tkinter import ttk  
from tkinter import messagebox   
from tkinter import filedialog   

gencfsversion="0.4"
encfsxml=".encfs6.xml" 
faviconname='favicon.gif'

class app_t():
##
# The constructor for the GUI application   
    def __init__(self):
        userpath=os.path.expanduser("~")          # check what user
        configdir=userpath+"/.GEncFs"
        if os.access(configdir, os.F_OK)==False:  # check if user has a directory containing persistent data
          os.mkdir(configdir,0o777)                         # if not create the directory
        configfile="conf"                            
        self.pathtoconfig=configdir+"/"+configfile
        if os.access(self.pathtoconfig, os.F_OK)==False:   # check if file exists containing persistent data
          os.system("touch "+self.pathtoconfig)               # if not create the empty file
          self.claim_filecontent(self.pathtoconfig)
        pathtoconfigfile=open(self.pathtoconfig) # now read the file containing persistent data or being empty
        pathstoencfs=pathtoconfigfile.readlines()  
        pathtoconfigfile.close()
        if len(pathstoencfs)==0:
            self.claim_filecontent(self.pathtoconfig)
        
        # the list box does not point to anything the last position is taken
        self.index='0'
        
        # setup the gui stuff
        self.window=Tk()
        self.window.title('Gui for EncFs')
        
        # add an icon
        img = PhotoImage(file=favicon)
        self.window.call('wm', 'iconphoto', self.window._w, img)
        
        # create the menus   
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
        self.window.label.pack()
        self.window.password=Entry(self.window, show='*')
        self.window.password.pack()
        
        # set up and register the buttons
        self.window.mountbutton=Button(master=self.window,text='Mount EncFs',command=self.encfsmount)
        self.window.mountbutton.pack()
        self.window.umountbutton=Button(master=self.window,text='Umount EncFs',command=self.encfsumount)
        self.window.umountbutton.pack()
        
        # set up the listbox and its label
        self.window.labelpath=Label(self.window, text='Path to the .crypt and crypt directories')
        self.window.labelpath.pack()
        self.window.listbox = Listbox(self.window,  width=50,  height=5,  selectmode=SINGLE)
        self.window.listbox.pack()
        for item in pathstoencfs:
          i=item.strip()  
          if len(i)>0:  
            self.window.listbox.insert(END, i)
        self.window.listbox.select_set(0)  # selects the first one, so something is selected    
        
        self.window.mainloop()
        
    def claim_filecontent(self, pathtoconfig):
         messagebox.showerror("Error","Configfile is empty. Add path to "+pathtoconfig+ " for .crypt and crypt")       
         self.window.destroy()
        
    def quit(self):
           self.window.destroy()
           
    def updateconfig(self):
        items=self.window.listbox.get(0, END)
        pathtoconfigfile=open(self.pathtoconfig,  'w') # now write the file containing persistent data
        for i in items:
            pathtoconfigfile.write(i+"\n")  
        pathtoconfigfile.close()
        
    def existconfig(self, n):
        items=self.window.listbox.get(0, END)
        value=False
        for i in items:
            if i==n:
                value=True
        return value        
 
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
         
    def remove(self):
        self.window.listbox.delete(ANCHOR)
        self.updateconfig()
           
    def about(self):
         messagebox.showinfo("About","Gencfs a gui front end for Encfs from https://www.linurs.org")       
           
    def encfsumount(self):
         i=self.window.listbox.curselection()
         if len(i)>0:
           self.index=i[0]
         pathtoencfs=self.window.listbox.get(self.index)
         cmd ="fusermount -u "+pathtoencfs+"/crypt"
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
         return 0
           
    def encfsmount(self):
         i=self.window.listbox.curselection()
         if len(i)>0:
          self.index=i[0]
         pathtoencfs=self.window.listbox.get(self.index)
         password=self.window.password.get()
         b=password.encode('utf-8')
         cmd ="encfs --stdinpass "+pathtoencfs+"/.crypt "+pathtoencfs+"/crypt" # call encfs without promting for password
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
         return 0     

    def create(self):
         i=self.window.listbox.curselection()
         if len(i)>0:
          self.index=i[0]
         pathtoencfs=self.window.listbox.get(self.index)
         if os.path.isdir(pathtoencfs)==False:
               messagebox.showinfo("Error","Directory "+pathtoencfs+" not found")
         else:      
             self.dcrypt=pathtoencfs+"/.crypt"
             self.crypt=pathtoencfs+"/crypt"
             if os.path.isdir(self.crypt)==False:
                    messagebox.showinfo("Info","Mounting point "+self.crypt+" will be created")       
                    os.mkdir(self.crypt) 
             if os.path.isdir(self.dcrypt)==True:
                    messagebox.showinfo("Info","Crypted directory "+self.dcrypt+" already exist")
                    xmlfile=self.dcrypt+"/"+encfsxml
                    if os.path.isfile(xmlfile)==True:  
                        messagebox.showinfo("Error","Crypted directory is not empty")             
                    else:
                        self.changepassword=False
                        self.newpassword()        
             else:
                    messagebox.showinfo("Info","Crypted directory "+self.dcrypt+" will be created")       
                    os.mkdir(self.dcrypt) 
                    self.changepassword=False
                    self.newpassword()          

    def newpassword(self):
           w=self.window.winfo_children() 
           childwindow=False
           for x in w:
               if x.widgetName=="toplevel":
                   childwindow=True
           if childwindow==False: # prevents that multiple child windows can open
           
               self.newpasswordwindow=Toplevel(master=self.window)
               self.newpasswordwindow.title('Password')
    
               self.askpasswordframe=LabelFrame(master=self.newpasswordwindow,
                                                 text="New Password")
               self.askpasswordframe.grid(column=0,  row=0)
    
             # the passwords
               self.newpassword1=StringVar()
               self.askportname=Entry(master=self.askpasswordframe,
                                           textvariable=self.newpassword1, show='*')
               self.askportname.grid(column=0,  row=0)
               self.newpassword2=StringVar()
               self.askportname=Entry(master=self.askpasswordframe,
                                           textvariable=self.newpassword2, show='*')
               self.askportname.grid(column=0,  row=1)
    
               # The ok button
               self.ok_askportbutton=Button(master=self.newpasswordwindow,
                                                  text='OK',
                                                  command=self.okpassword)
               self.ok_askportbutton.grid(column=0,
                                             row=2,
                                             sticky=W)
               # The cancel button
               self.cancel_askportbutton=Button(master=self.newpasswordwindow,
                                                  text='CANCEL',
                                                  command=self.cancelpassword)
               self.cancel_askportbutton.grid(column=0,
                                                 row=3,
                                                 sticky=W)
    
    def okpassword(self):
        self.newpasswordwindow.destroy()
        p1=self.newpassword1.get()+'\n'
        p2=self.newpassword2.get()+'\n'
        newb=p1.encode('utf-8')
        if(p1 != p2):
             messagebox.showinfo("Error","Passwords do not match")       
        elif self.changepassword==False:  # create new directory
            cmd ="encfs --stdinpass --standard "+self.dcrypt+" "+self.crypt # call encfs to create and mount the crypted directory
            args=shlex.split(cmd)
            
            p = subprocess.Popen(args,  
                              stdin=subprocess.PIPE, 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, # standard err are passed to stdout
                              ) # open new process
           
            stdout_value, stderr_value = p.communicate(newb) # communicate is a one time action, afterwards p is closed
            xmlfile=self.dcrypt+"/"+encfsxml
            if os.path.isfile(xmlfile)==True:  
                    messagebox.showinfo("Info","Successfully created\n"+stdout_value.decode("utf-8"))
            else:
                    messagebox.showinfo("Error","Failed to create\n"+stdout_value.decode("utf-8") )       
        else:   # change password on existing directory       
            if expect==True:
                 # make sure it is unmounted 
                 cmd ="fusermount -u "+self.crypt
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
                 child = pexpect.spawn("encfsctl passwd "+self.dcrypt)
                 try:
                    child.expect("EncFS Password: ", timeout=2)
                 except:
                       messagebox.showinfo("Error",str(child))
                 child.sendline(b)             
                 try:
                    child.expect("New Encfs Password: ", timeout=2)
                 except:
                    pass
                 if child.terminated==False:
                     child.sendline(p1)
                     try:
                            child.expect("Verify Encfs Password: ", timeout=2)
                     except:
                           messagebox.showinfo("Error",str(child))    
                     child.sendline(p2)
                 before=child.before
                 messagebox.showinfo("Info",before.decode("utf-8"))   
            else:
                 messagebox.showinfo("Error","pexpect is not installed but required for password change. https://pexpect.readthedocs.io \n") 
                         
    def cancelpassword(self):
        self.newpasswordwindow.destroy()
         
    def passwd(self):
         i=self.window.listbox.curselection()
         if len(i)>0:
          self.index=i[0]
         pathtoencfs=self.window.listbox.get(self.index)
         self.dcrypt=pathtoencfs+"/.crypt"
         self.crypt=pathtoencfs+"/crypt"
 
         self.changepassword=True
         self.newpassword()       

if __name__ == "__main__":
      ## manage the command line parameters
    # sets default values to variables and modifies their content according the command line parameter passed
    # additionally it handles the -h and --help command line parameter automatically
    parser = argparse.ArgumentParser(
                                     description='modme - A modbus py application', 
                                     epilog='urs@linurs.org')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s '+gencfsversion)
    parser.add_argument('-d', '--debug',   help="print debug messages",   action='store_true')  

    # the command line arguments passed
    args = parser.parse_args()      
    
    # Configuring the logger. Levels are DEBUG, INFO, WARNING, ERROR and CRITICAL
    # the parameter filename='example.log' would write it into a file
    logging.basicConfig() # init logging 
    logger = logging.getLogger() # get the root logger 
    if args.debug==True:
        logger.setLevel(logging.DEBUG)    # the level producing debug messagesl
    else:    
        logger.setLevel(logging.WARNING)
    logger.debug('Logging debug messages')
    
    # stuff to be logged before the logger came alive
    if expect==False:
         logger.debug('Packet pexpectl not found')
    
    # pyinstaller stuff required to create bundled versions as for windows exe:      
    frozen = 'not '
    if getattr(sys, 'frozen', False): # pyinstaller adds the name frozen to sys 
            frozen = ''  # we are running in a bundle (frozen)
            bundle_dir = sys._MEIPASS  # temporary folder of pyinstaller
    else:
            bundle_dir = os.path.dirname(os.path.abspath(__file__))   # we are running in a normal Python environment 
   
    logging.debug('Script is '+frozen+'frozen')
    logging.debug('Bundle dir is '+bundle_dir )
    logging.debug('sys.argv[0] is '+sys.argv[0] )
    logging.debug('sys.executable is '+sys.executable )
    logging.debug('os.getcwd is '+os.getcwd() )

# makes that the files are found
    favicon=bundle_dir+os.sep+faviconname    
    
    app=app_t()
