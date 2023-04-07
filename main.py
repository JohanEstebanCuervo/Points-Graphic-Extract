import os
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class App(tk.Tk):

    def __init__(self) -> None:
        super().__init__()
        self.__create_widgets()
        self.path = None
        self.image = None
        self.coords_plain = None
        self.images = []
        self.points = []
        self.index = 0

        self.names = []
        self.sheets = []
        self.mainloop()

    def __create_widgets(self):
        
        self.frame_controls = tk.Frame(self)
        self.frame_controls.grid(column=1,row=1)

        self.bt_load_folder = tk.Button(self.frame_controls, text='Cargar carpeta', command=self.load_folder)
        self.bt_load_folder.pack(side='left')
        self.bt_next_image = tk.Button(self.frame_controls, text='siguiente imagen', command=self.next_image)
        self.bt_next_image.pack(side='left')

        self.bt_next_image = tk.Button(self.frame_controls, text='Eliminar punto', command=self.delete_point)
        self.bt_next_image.pack(side='left')

        self.bt_save_points = tk.Button(self.frame_controls, text='Guardar puntos', command=self.save_points)
        self.bt_save_points.pack(side='left')

        self.bt_save_excel = tk.Button(self.frame_controls, text='Guardar Excel', command=self.save_excel)
        self.bt_save_excel.pack(side='left')

        self.lb_name_image = tk.Label(self.frame_controls, text='')
        self.lb_name_image.pack(side='right')

        self.canvas = tk.Canvas(self, width=1200, height=730, background='white')
        self.canvas.grid(column=1, row=2)
        self.canvas.bind("<Motion>", self.motion_mouse)
        self.canvas.bind("<Button-1>", self.point)

    def save_points(self):

        if len(self.points) <= 2:
            return
        
        points = np.array(self.points[2:], dtype=float)[:,:-1]

        point_init = self.points[0]
        point_end = self.points[1]
        points[:,0] = (points[:,0] - point_init[0])/(point_end[0]-point_init[0])
        points[:,1] = (point_init[1] - points[:,1])/(point_init[1]-point_end[1])

        points[:,0] *= (self.coords_plain[2] - self.coords_plain[0])
        points[:,1] *= (self.coords_plain[3] - self.coords_plain[1])

        points[:,0] += self.coords_plain[0]
        points[:,1] += self.coords_plain[1]

        plt.plot(points[:,0], points[:,1])
        plt.title('Grafica resultante')
        plt.grid()
        plt.show()

        df = pd.DataFrame(points)

        self.sheets.append(df)
        self.names.append(self.lb_name_image.cget('text'))
    
    def save_excel(self):
        writer = pd.ExcelWriter('Results.xlsx', engine='xlsxwriter')

        with pd.ExcelWriter('Results.xlsx', engine='xlsxwriter') as writer:
            for indexs, df in enumerate(self.sheets):
                df.to_excel(writer, sheet_name = self.names[indexs], index= False)

    def delete_point(self):
        if not self.points:
            return

        id = self.points.pop()[-1]

        self.canvas.delete(id)

    def point(self, event):
        
        if len(self.points) >= 2:
            color = 'red'

        else:
            color = 'green'

        x = event.x
        y=event.y
        id = self.canvas.create_oval(x-2, y-2, x+2,y+2, fill=color)
        self.points.append([x,y,id])

        if len(self.points ) == 2:
            self.coords_capture()

    def coords_capture(self):
        
        init_x = simpledialog.askfloat(prompt='Inicial X',initialvalue=400, title='Inicial X', parent=self)
        init_y = simpledialog.askfloat(prompt='Inicial Y', initialvalue=0, title='Inicial Y', parent=self)
        end_x = simpledialog.askfloat(prompt='Final X', initialvalue=800, title='Final X', parent=self)
        end_y = simpledialog.askfloat(prompt='Final Y', initialvalue=1, title='Final Y', parent=self)

        self.coords_plain = (init_x, init_y, end_x, end_y)

    def next_image(self):
        self.canvas.delete("all")
        self.points = []
        self.show_image(self.index + 1)

    def load_folder(self):

        self.path = filedialog.askdirectory(title='Carpeta con las imagenes')

        images = []

        for file in os.listdir(self.path):
            if file.upper().endswith('.PNG'):
                images.append(self.path + '/' + file)

        self.images = images
        self.show_image(0)

    def show_image(self, index: int):

        if len(self.images) == 0:
            return

        if index >= len(self.images):
            index = 0
        
        path = self.images[index]
        image = Image.open(path)
        image = image.resize((1000,800), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.image, anchor="nw")
        self.index = index

        text = path[path.rfind('/') + 1:]
        self.lb_name_image.config(text=text)

    def motion_mouse(self, event):

        self.title(f"{event.x} - {event.y}")

if __name__ == '__main__':

    App()
