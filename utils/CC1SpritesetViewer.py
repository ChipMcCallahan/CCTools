import tkinter as tk
from PIL import Image, ImageTk

from cc_tools import CC1
from cc_tools.cc1_sprite_set import CC1SpriteSet


class CC1SpritesetViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.configure(bg='black')  # Set the background color
        self.geometry("300x600")  # Set the window size to 800x600
        self.title("CC1 Sprite Viewer")

        self.sprite_sets = CC1SpriteSet.create_sprite_sets()

        # Sort sprite sets by size
        self.sorted_sprite_sets = sorted(self.sprite_sets.items(), key=lambda x: x[1].get_size_in_pixels())

        self.setup_ui()

    def setup_ui(self):
        list_frame = tk.Frame(self)
        list_frame.pack(side="left", fill="y")

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        for elem in CC1:
            self.listbox.insert(tk.END, elem.name)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        image_frame = tk.Frame(self, bg="black")
        image_frame.pack(side="right", fill="both", expand=True)

        self.image_frames = []
        for sprite_set_name, sprite_set in self.sorted_sprite_sets:
            frame = tk.Frame(image_frame, bg='black')
            frame.pack(side="top", fill="x")

            label_image = tk.Label(frame, bg="black")
            label_image.pack(side="left")

            label_name = tk.Label(frame, text=sprite_set_name, bg="black", fg="white")
            label_name.pack(side="right")

            self.image_frames.append((label_image, sprite_set))

        self.listbox.bind("<<ListboxSelect>>", self.update_images)

    def update_images(self, event):
        if not self.listbox.curselection():
            return

        selected_key = self.listbox.get(self.listbox.curselection())
        for label_image, sprite_set in self.image_frames:
            pil_image = sprite_set.get_sprite(selected_key)
            tk_image = ImageTk.PhotoImage(pil_image)
            label_image.config(image=tk_image)
            label_image.image = tk_image  # Keep a reference


if __name__ == "__main__":
    app = CC1SpritesetViewer()
    app.mainloop()
