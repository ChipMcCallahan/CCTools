import tkinter as tk
from tkinter import filedialog, Menu
from PIL import Image, ImageTk
from src.cc_tools.cc1_sprite_set import CC1SpriteSet  # Adjust the import path as needed
from src.cc_tools.cc1 import CC1


class CC1SpriteViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CC1 Sprite Viewer")
        self.geometry("800x600")  # Set the window size to 800x600
        self.configure(bg='black')  # Set the background color to white
        self.sprite_set = None
        self.current_sprite = None
        self.current_key = CC1.FLOOR
        self.enum_members = list(CC1.valid())
        self.sprite_name_label = None
        self.sprite_image_label = None
        self.magnified_image_label = None
        self.menu_bar = None
        self.file_menu = None
        self.available_sets = CC1SpriteSet.available_sprite_sets()
        self.init_ui()

    def init_ui(self):
        self.menu_bar = Menu(self)
        self.file_menu = Menu(self.menu_bar, tearoff=0)

        for set_name in self.available_sets.keys():
            self.file_menu.add_command(label=set_name,
                                       command=lambda name=set_name: self.load_sprite_set(name))
        self.menu_bar.add_cascade(label="File", menu=self.file_menu) #submenu within a menu
        self.config(menu=self.menu_bar)

        self.sprite_name_label = tk.Label(self, text="")
        self.sprite_name_label.pack()

        self.sprite_image_label = tk.Label(self)
        self.sprite_image_label.pack()

        self.magnified_image_label = tk.Label(self)
        self.magnified_image_label.pack()

        self.bind("<Left>", self.previous_sprite)
        self.bind("<Right>", self.next_sprite)

    def load_sprite_set(self, setname):
        self.sprite_set = self.available_sets[setname]
        self.update_sprite()

    def update_sprite(self):
        if self.sprite_set and self.current_key:
            sprite = self.sprite_set.get_sprite(self.current_key)

            self.sprite_name_label.config(text=str(self.current_key))

            raw_image = ImageTk.PhotoImage(sprite)
            self.sprite_image_label.config(image=raw_image)
            self.sprite_image_label.image = raw_image

            magnified_image = ImageTk.PhotoImage(
                sprite.resize((sprite.width * 8, sprite.height * 8), Image.NEAREST))
            self.magnified_image_label.config(image=magnified_image)
            self.magnified_image_label.image = magnified_image

    def next_sprite(self, event):
        current_index = self.enum_members.index(self.current_key)
        next_index = (current_index + 1) % len(self.enum_members)
        self.current_key = self.enum_members[next_index]
        self.update_sprite()

    def previous_sprite(self, event):
        current_index = self.enum_members.index(self.current_key)
        prev_index = (current_index - 1) % len(self.enum_members)
        self.current_key = self.enum_members[prev_index]
        self.update_sprite()


if __name__ == "__main__":
    app = CC1SpriteViewer()
    app.mainloop()
