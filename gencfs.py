#!/usr/bin/python3

## @package gencfs 
# @author urs lindegger urs@linurs.org  

## @todo 
# - doxygen
# - change password, 3 steps, current password, new and verify
#
#
# Bug fixes and improvements from previous version:
# ---------------------------------------------------
# 
#  From Version 0.5 to 0.6
# -----------------------
# - added menu to add/create fs and change password
#
#  From Version 0.4 to 0.5
# -----------------------
# - added window icon
# - used global index variable to not loose listboxfocus
#
# From Version 0.3 to 0.4
# -----------------------
# - support multiple 
#
# From Version 0.2 to 0.3
# -----------------------
# - porting to python3
#
# From Version 0.1 to 0.2
# -----------------------
# - popen4 does not work anymore since it is deprecated and replaced by subprocess module 
#   as a guideline http://www.doughellmann.com/PyMOTW/subprocess/ has been used
# 

## @mainpage gencfs
# gencfs is a simple gui for encfs
# 

import os
import subprocess
import shlex

import tkinter 
import tkinter.messagebox 
import tkinter.filedialog

class App():
##
# The constructor for the GUI application   
    def __init__(self):
        userpath=os.path.expanduser("~")          # check what user
        configdir=userpath+"/.GEncFs"
        if os.access(configdir, os.F_OK)==False:  # check if user has a directory containing persistent data
          os.mkdir(configdir,0o777)               # if not create the directory
        configfile="conf"                            
        self.pathtoconfig=configdir+"/"+configfile
        if os.access(self.pathtoconfig, os.F_OK)==False:   # check if file exists containing persistent data
          os.system("touch "+self.pathtoconfig)            # if not create the empty file
          self.claim_filecontent(self.pathtoconfig)
        pathtoconfigfile=open(self.pathtoconfig) # now read the file containing persistent data or being empty
        pathstoencfs=pathtoconfigfile.readlines()  
        pathtoconfigfile.close()
        if len(pathstoencfs)==0:
            self.claim_filecontent(self.pathtoconfig)
        
        # the list box does not point to anything the last position is taken
        self.index='0'
        
        # setup the gui stuff
        self.window=tkinter.Tk()
        self.window.title('Gui for EncFs')
        
        # add an icon
        img = tkinter.PhotoImage(file='favicon.gif')
        self.window.call('wm', 'iconphoto', self.window._w, img)
        
        # create the menus   
        self.menubar = tkinter.Menu(self.window)
        filemenu = tkinter.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Add directory where .crypt and crypt is to list", command=self.add)
        filemenu.add_command(label="create .crypt and crypt", command=self.create)
        filemenu.add_separator()
        filemenu.add_command(label="Change Password", command=self.passwd)
        filemenu.add_command(label="Remove from list", command=self.remove)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)
        self.menubar.add_command(label="About", command=self.about)
        self.window.config(menu=self.menubar)
        
        # add the password label and entry field
        self.window.label=tkinter.Label(self.window, text='Password')
        self.window.label.pack()
        self.window.password=tkinter.Entry(self.window, show='*')
        self.window.password.pack()
        
        # set up and register the buttons
        self.window.mountbutton=tkinter.Button(master=self.window,text='Mount EncFs',command=self.encfsmount)
        self.window.mountbutton.pack()
        self.window.umountbutton=tkinter.Button(master=self.window,text='Umount EncFs',command=self.encfsumount)
        self.window.umountbutton.pack()
        
        # set up the listbox and its label
        self.window.labelpath=tkinter.Label(self.window, text='Path to the .crypt and crypt directories')
        self.window.labelpath.pack()
        self.window.listbox = tkinter.Listbox(self.window,  width=50,  height=5,  selectmode=tkinter.SINGLE)
        self.window.listbox.pack()
        for item in pathstoencfs:
          i=item.strip()  
          if len(i)>0:  
            self.window.listbox.insert(tkinter.END, i)
        self.window.listbox.select_set(0)  # selects the first one, so something is selected    
        
        self.window.mainloop()
        
    def claim_filecontent(self, pathtoconfig):
         tkinter.messagebox.showerror("Error","Configfile is empty and Gencfs does not know what to do. Please add the paths where .crypt and .crypt is to "+pathtoconfig)       
         self.window.destroy()
        
    def quit(self):
           self.window.destroy()
           
    def updateconfig(self):
        pass
        items=self.window.listbox.get(0, tkinter.END)
        pathtoconfigfile=open(self.pathtoconfig,  'w') # now write the file containing persistent data
        for i in items:
            pathtoconfigfile.write(i+"\n")  
        pathtoconfigfile.close()
 
    def add(self):
        dname = tkinter.filedialog.askdirectory(initialdir='~')   
        self.window.listbox.insert(tkinter.END, dname)
        self.updateconfig()
                         
    def remove(self):
        pass       
        self.window.listbox.delete(tkinter.ANCHOR)
        self.updateconfig()
           
    def about(self):
         tkinter.messagebox.showinfo("About","Gencfs a gui front end for Encfs")       
           
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
          tkinter.messagebox.showinfo("umount","Successfully umounted")
         else:  
          tkinter.messagebox.showinfo("umount",stdout_value)
         return 0
           
    def encfsmount(self):
         i=self.window.listbox.curselection()
         if len(i)>0:
          self.index=i[0]
         pathtoencfs=self.window.listbox.get(self.index)
         password=self.window.password.get()
         cmd ="encfs --stdinpass "+pathtoencfs+"/.crypt "+pathtoencfs+"/crypt" # call encfs without promting for password
         args=shlex.split(cmd)
         
         p = subprocess.Popen(args,  
                              stdin=subprocess.PIPE, 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, # standard err are passed to stdout
                              ) # open new process
         b=password.encode('utf-8')
         stdout_value, stderr_value = p.communicate(b) # communicate is a one time action, afterwards p is closed
         if (stdout_value==b''):
          tkinter.messagebox.showinfo("mount","Successfully mounted")
         else: 
          tkinter.messagebox.showinfo("mount",stdout_value)
         return 0     
         
         
    def create(self):
         i=self.window.listbox.curselection()
         if len(i)>0:
          self.index=i[0]
         pathtoencfs=self.window.listbox.get(self.index)
    #     password=self.window.password.get()
         cmd ="encfs --standard "+pathtoencfs+"/.crypt "+pathtoencfs+"/crypt" # call encfs without promting for password
         args=shlex.split(cmd)
         
         p = subprocess.Popen(args,  
                              stdin=subprocess.PIPE, 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, # standard err are passed to stdout
                              ) # open new process
  #       b=password.encode('utf-8')
         b='y'.encode('utf-8')
         stdout_value, stderr_value = p.communicate(b) # communicate is a one time action, afterwards p is closed
         if (stdout_value==b''):
          tkinter.messagebox.showinfo("mount","Successfully mounted")
         else: 
          tkinter.messagebox.showinfo("mount",stdout_value)
         return 0         
         
         
    def passwd(self):
         i=self.window.listbox.curselection()
         if len(i)>0:
          self.index=i[0]
         pathtoencfs=self.window.listbox.get(self.index)
         #password=self.window.password.get()
         tkinter.messagebox.showinfo("mount","selected "+pathtoencfs)
            

## Main program, get persistent data as path to encfs 
if __name__ == "__main__":
    App()
