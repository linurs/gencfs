#!/usr/bin/python
# Gui to mount encfs
# to do:
#   check better if password and path are empty
# changed:
# spelling error removed from the gui
import os
import tkMessageBox 
import Tkinter 

mountflag=0 
pathtoencfs=""

def encfsmount():
 global mountflag
 global pathtoencfs
 password=window.password.get()
 pathtoencfs=window.pathencfs.get()
 cmd ="encfs "+pathtoencfs+"/.crypt "+pathtoencfs+"/crypt"
 pout,  pin =os.popen4(cmd)
 pout.write(password)
 pout.close()
 childresp=pin.readline() # get password prompt
 childresp=pin.readline() # get response (error)
 pin.close()
 if len(childresp)==0:
  tkMessageBox.showinfo("mount","Successfully mounted")
  mountflag=1
  window.mountbutton.config(relief=Tkinter.SUNKEN)
  window.umountbutton.config(relief=Tkinter.RAISED)
 else: 
  tkMessageBox.showinfo("mount",childresp)
 return 0  
	
def encfsumount():
 global mountflag
 global pathtoencfs
 pathtoencfs=window.pathencfs.get()
 cmd ="fusermount -u "+pathtoencfs+"/crypt"
 pout,  pin =os.popen4(cmd)
 pout.close()
 childresp=pin.readline()
 pin.close()
 if len(childresp)==0:
  tkMessageBox.showinfo("umount","Successfully umounted")
  mountflag=0
  window.umountbutton.config(relief=Tkinter.SUNKEN)
  window.mountbutton.config(relief=Tkinter.RAISED)
 else: 
  tkMessageBox.showinfo("umount",childresp)
 return 0

# Main program, get persistent data as path to encfs 

#maybe do not create the files here do it on exit
userpath=os.path.expanduser("~")     # check what user
configdir=userpath+"/.GEncFs"
if os.access(configdir, os.F_OK)==False:  # check if user has a directory containing persistent data
  os.mkdir(configdir,0777)                   # if not create the directory
configfile="conf"                            
pathtoconfig=configdir+"/"+configfile
if os.access(pathtoconfig, os.F_OK)==False:   # check if file exists containing persistent data
#  os.chdir(configdir)
  os.system("touch "+pathtoconfig) # if not create the empty file
pathtoconfigfile=file(pathtoconfig,'r') # now read the file containing persistent data or being empty
pathtoencfscr=pathtoconfigfile.readline()
pathtoencfs=pathtoencfscr.strip('\n')
pathtoconfigfile.close()
 
window=Tkinter.Tk()
window.title('Gui for EncFs')
window.label=Tkinter.Label(window, text='Password')
window.label.pack()

window.password=Tkinter.Entry(window, show='*')
window.password.pack()

window.mountbutton=Tkinter.Button(master=window,text='Mount EncFs',command=encfsmount)
window.mountbutton.pack()

window.umountbutton=Tkinter.Button(master=window,text='Umount EncFs',relief=Tkinter.SUNKEN, command=encfsumount)
window.umountbutton.pack()

window.labelpath=Tkinter.Label(window, text='Path to the .crypt and crypt directories')
window.labelpath.pack()

window.pathencfs=Tkinter.Entry(window, width=50)
window.pathencfs.pack()
window.pathencfs.insert(0, pathtoencfs)

window.mainloop()

cmd="echo "+pathtoencfs+" > "+configdir+"/"+configfile
os.system(cmd)
