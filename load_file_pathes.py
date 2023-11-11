from tkinter import *
from tkinter import filedialog
# import filedialog

def Quit(ev):
    global root
    root.destroy()
    
def LoadFile(ev): 
    fn = filedialog.Open(root).show()
    if fn == '':
        return
    textbox.delete('1.0', 'end') 
    textbox.insert('1.0', fn)

root = Tk()

panelFrame = Frame(root, height = 60, bg = 'gray')
textFrame = Frame(root, height = 340, width = 600)

panelFrame.pack(side = 'top', fill = 'x')
textFrame.pack(side = 'bottom', fill = 'both', expand = 1)

textbox = Text(textFrame, font='Arial 14', wrap='word')
scrollbar = Scrollbar(textFrame)

scrollbar['command'] = textbox.yview
textbox['yscrollcommand'] = scrollbar.set

textbox.pack(side = 'left', fill = 'both', expand = 1)
scrollbar.pack(side = 'right', fill = 'y')

loadBtn = Button(panelFrame, text = 'Load')
saveBtn = Button(panelFrame, text = 'Save')
quitBtn = Button(panelFrame, text = 'Quit')

loadBtn.bind("<Button-1>", LoadFile)
quitBtn.bind("<Button-1>", Quit)

loadBtn.place(x = 10, y = 10, width = 40, height = 40)
saveBtn.place(x = 60, y = 10, width = 40, height = 40)
quitBtn.place(x = 110, y = 10, width = 40, height = 40)

root.mainloop()