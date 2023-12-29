import tkinter as tk
from tkinter import filedialog, Menu
from PIL import Image, ImageTk
import importlib.resources
from cc_tools import DATHandler, CC1LevelImager  # Adjust the import path as needed


class CC1LevelViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CC1 Level Viewer")
        self.geometry("800x600")  # Adjust as needed
        self.menu_bar = None
        self.file_menu = None
        self.level_title_label = None
        self.level_image_label = None
        self.level_set = None
        self.current_level_index = 0
        self.level_imager = CC1LevelImager("8x8")  # Assuming CC1LevelImager is already initialized with sprite set
        self.init_ui()

    def init_ui(self):
        # Menu for opening level sets
        self.menu_bar = Menu(self)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open Level Set", command=self.load_level_set)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.config(menu=self.menu_bar)

        # Labels for level title and image
        self.level_title_label = tk.Label(self, text="")
        self.level_title_label.pack()
        self.level_image_label = tk.Label(self)
        self.level_image_label.pack()

        self.bind("<Left>", self.previous_level)
        self.bind("<Right>", self.next_level)

    def load_level_set(self):
        # Use importlib.resources to get the package directory
        with importlib.resources.path('cc_tools.sets', '') as package_dir:
            file_path = filedialog.askopenfilename(initialdir=str(package_dir))  # Use the package directory path

        if file_path:
            self.level_set = DATHandler.read(file_path)
            self.display_level()

    def display_level(self):
        if self.level_set and 0 <= self.current_level_index < len(self.level_set.levels):
            level = self.level_set.levels[self.current_level_index]
            self.level_title_label.config(text=level.title)
            level_image = self.level_imager.image8(level)
            tk_image = ImageTk.PhotoImage(level_image)
            self.level_image_label.config(image=tk_image)
            self.level_image_label.image = tk_image  # Keep a reference

    def next_level(self, event):
        if self.level_set and self.current_level_index < len(self.level_set.levels) - 1:
            self.current_level_index += 1
            self.display_level()

    def previous_level(self, event):
        if self.level_set and self.current_level_index > 0:
            self.current_level_index -= 1
            self.display_level()


if __name__ == "__main__":
    app = CC1LevelViewer()
    app.mainloop()
