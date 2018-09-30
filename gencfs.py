#!/usr/bin/python3

## @package gencfs 
# @author urs lindegger urs@linurs.org  

## @todo 
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

import tkinter 
import tkinter.messagebox 
import tkinter.filedialog


encfsxml=".encfs6.xml" 

class App():
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
        self.window=tkinter.Tk()
        self.window.title('Gui for EncFs')
        
        # add an icon
        img = tkinter.PhotoImage(file='favicon.gif')
        self.window.call('wm', 'iconphoto', self.window._w, img)
        
        # create the menus   
        self.menubar = tkinter.Menu(self.window)
        filemenu = tkinter.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Add directory for .crypt and crypt", command=self.add)
        filemenu.add_command(label="Remove directory", command=self.remove)
        filemenu.add_command(label="Create .crypt and crypt", command=self.create)
        filemenu.add_separator()
        filemenu.add_command(label="Change Password", command=self.passwd)
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
         tkinter.messagebox.showerror("Error","Configfile is empty. Add path to "+pathtoconfig+ " for .crypt and crypt")       
         self.window.destroy()
        
    def quit(self):
           self.window.destroy()
           
    def updateconfig(self):
        items=self.window.listbox.get(0, tkinter.END)
        pathtoconfigfile=open(self.pathtoconfig,  'w') # now write the file containing persistent data
        for i in items:
            pathtoconfigfile.write(i+"\n")  
        pathtoconfigfile.close()
        
    def existconfig(self, n):
        items=self.window.listbox.get(0, tkinter.END)
        value=False
        for i in items:
            if i==n:
                value=True
        return value        
 
    def add(self):
        dname = tkinter.filedialog.askdirectory(initialdir='~')   
        if self.existconfig(dname)==True:
                  tkinter.messagebox.showinfo("Info","Directory "+dname+" already exists in the list")       
        else:
            if os.path.isdir(dname)==False:
                tkinter.messagebox.showinfo("Info","Directory "+dname+" does not exist and will be created")       
                os.mkdir(dname)
            self.window.listbox.insert(tkinter.END, dname)
            self.updateconfig()  
         
    def remove(self):
        self.window.listbox.delete(tkinter.ANCHOR)
        self.updateconfig()
           
    def about(self):
         tkinter.messagebox.showinfo("About","Gencfs a gui front end for Encfs from https://www.linurs.org")       
           
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
          tkinter.messagebox.showinfo("mount","Successfully mounted")
         else: 
          tkinter.messagebox.showinfo("mount",stdout_value)
         return 0     

    def newpassword(self):
           w=self.window.winfo_children() 
           childwindow=False
           for x in w:
               if x.widgetName=="toplevel":
                   childwindow=True
           if childwindow==False: # prevents that multiple child windows can open
           
               self.newpasswordwindow=tkinter.Toplevel(master=self.window)
               self.newpasswordwindow.title('Password')
    
               self.askpasswordframe=tkinter.LabelFrame(master=self.newpasswordwindow,
                                                 text="New Password")
               self.askpasswordframe.grid(column=0,  row=0)
    
             # the passwords
               self.newpassword1=tkinter.StringVar()
               self.askportname=tkinter.Entry(master=self.askpasswordframe,
                                           textvariable=self.newpassword1, show='*')
               self.askportname.grid(column=0,  row=0)
               self.newpassword2=tkinter.StringVar()
               self.askportname=tkinter.Entry(master=self.askpasswordframe,
                                           textvariable=self.newpassword2, show='*')
               self.askportname.grid(column=0,  row=1)
    
               # The ok button
               self.ok_askportbutton=tkinter.Button(master=self.newpasswordwindow,
                                                  text='OK',
                                                  command=self.okpassword)
               self.ok_askportbutton.grid(column=0,
                                             row=2,
                                             sticky=tkinter.W)
               # The cancel button
               self.cancel_askportbutton=tkinter.Button(master=self.newpasswordwindow,
                                                  text='CANCEL',
                                                  command=self.cancelpassword)
               self.cancel_askportbutton.grid(column=0,
                                                 row=3,
                                                 sticky=tkinter.W)
    
    def okpassword(self):
        self.newpasswordwindow.destroy()
        p1=self.newpassword1.get()+'\n'
        p2=self.newpassword2.get()+'\n'
        newb=p1.encode('utf-8')
        if(p1 != p2):
             tkinter.messagebox.showinfo("Error","Passwords do not match")       
        elif self.changepassword==False:
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
                    tkinter.messagebox.showinfo("Info","Successfully created\n")
            else:
                    tkinter.messagebox.showinfo("Error","Failed to create\n"+stdout_value)        
        else:          
 
             # make sure it is unmounte 
             cmd ="fusermount -u "+self.crypt
             args=shlex.split(cmd)
             p = subprocess.Popen(args, 
                                  stdin=subprocess.PIPE, 
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, # standard err are passed to stdout
                                  ) # open new process
             stdout_value, stderr_value = p.communicate()# communicate is a one time action, afterwards p is closed 

             password=self.window.password.get()
             b=password.encode('utf-8')
             cmd ="encfsctl passwd "+self.dcrypt
             args=shlex.split(cmd)
                                     
             proc = subprocess.Popen(args,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
 
             proc.stdin.write(b+b'\n')   
             proc.stdin.flush()
             r=proc.stdout.readline()     
             
             proc.stdin.write(newb+b'\n') 
             proc.stdin.flush()
             r=proc.stdout.readline()    
    
             proc.stdin.write(newb+b'\n') 
             proc.stdin.flush()
             r=r+proc.stdout.readline()
             
             proc.stdin.close()
             proc.terminate()
             proc.wait(timeout=0.5)
        
    def cancelpassword(self):
        self.newpasswordwindow.destroy()
         
    def create(self):
         i=self.window.listbox.curselection()
         if len(i)>0:
          self.index=i[0]
         pathtoencfs=self.window.listbox.get(self.index)
         if os.path.isdir(pathtoencfs)==False:
               tkinter.messagebox.showinfo("Error","Directory "+pathtoencfs+" not found")
         else:      
             self.dcrypt=pathtoencfs+"/.crypt"
             self.crypt=pathtoencfs+"/crypt"
             if os.path.isdir(self.crypt)==False:
                    tkinter.messagebox.showinfo("Info","Mounting point "+self.crypt+" will be created")       
                    os.mkdir(self.crypt) 
             if os.path.isdir(self.dcrypt)==True:
                    tkinter.messagebox.showinfo("Info","Crypted directory "+self.dcrypt+" already exist")
                    xmlfile=self.dcrypt+"/"+encfsxml
                    if os.path.isfile(xmlfile)==True:  
                        tkinter.messagebox.showinfo("Error","Crypted directory is not empty")             
                    else:
                        self.changepassword=False
                        self.newpassword()        
             else:
                    tkinter.messagebox.showinfo("Info","Crypted directory "+self.dcrypt+" will be created")       
                    os.mkdir(self.dcrypt) 
                    self.changepassword=False
                    self.newpassword()        

    def passwd(self):
         i=self.window.listbox.curselection()
         if len(i)>0:
          self.index=i[0]
         pathtoencfs=self.window.listbox.get(self.index)
         self.dcrypt=pathtoencfs+"/.crypt"
         self.crypt=pathtoencfs+"/crypt"
 
         self.changepassword=True
         self.newpassword()       

## Main program, get persistent data as path to encfs 
if __name__ == "__main__":
    App()
