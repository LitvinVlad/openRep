from tkinter import *
from tkinter import filedialog

from video_info import * 

class MainApplication(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.Scrol = Scrollbar(self.parent)
        self.Text = Text(self.parent, font='Arial 18', wrap='word', state="disabled")

        panelFrame = Frame(self.parent, height = 65, bg = 'gray')
        textFrame = Frame(self.parent, height = 340, width = 600)

        panelFrame.pack(side = 'top', fill = 'x')
        textFrame.pack(side = 'bottom', fill = 'both', expand = 1)

        self.Scrol.config(command=self.Text.yview)
        self.Text.config(yscrollcommand=self.Scrol.set)

        self.Text.bind("<Double-Button-1>", self.deleteLine)

        self.Scrol['command'] = self.Text.yview
        self.Text['yscrollcommand'] = self.Scrol.set

        self.Text.pack(side = 'left', fill = 'both', expand = 1)
        self.Scrol.pack(side = 'right', fill = 'y')

        self.loadBtn = Button(panelFrame, font='Arial 18', text = 'Загрузить файл')
        self.analyzeVideoBtn = Button(panelFrame, font='Arial 18', text = 'Начать обработку файла(ов)')
        self.quitBtn = Button(panelFrame, font='Arial 18', text = 'Выйти')

        self.loadBtn.bind("<Button-1>", self.LoadFile)
        self.analyzeVideoBtn.bind("<Button-1>", self.AnalyzeVideo)
        self.quitBtn.bind("<Button-1>", self.Quit)

        self.loadBtn.place(x = 10, y = 10, width = 250, height = 50)
        self.analyzeVideoBtn.place(x = 270, y = 10, width = 350, height = 50)
        self.quitBtn.place(x = 630, y = 10, width = 200, height = 50)


    def LoadFile(self, event): 
        new_files_group = filedialog.askopenfilenames(parent=root)
        if not new_files_group:
            return
        
        files_added = False

        for new_file_path in new_files_group:
            if (new_file_path not in path_list_set):
                files_added = True
                path_list_set.add(new_file_path)
                path_list.append(new_file_path)

        if files_added:
            self.Text.config(state='normal')
            self.Text.delete('1.0', 'end') 
            self.Text.insert('1.0', '\n'.join(tmp_path for tmp_path in path_list))
            self.Text.config(state='disabled')
         
    def deleteLine(self, event):
        x = self.Text.get('current linestart', 'current lineend+1c')
        self.Text.config(state='normal')
        self.Text.delete('current linestart', 'current lineend+1c')     
        self.Text.config(state='disabled')
        x = x[:-1]
        path_list.remove(x)
        path_list_set.remove(x)
        return "break" # uncomment if you want to disable selection caused by double-clicking

    def Quit(self, event):
        global root
        root.destroy()

    def AnalyzeVideo(self, event):
        for file_path in path_list:
            get_video_info(file_path)
        return

path_list = []
path_list_set = set()

root = Tk()
app = MainApplication(root)
root.mainloop()
