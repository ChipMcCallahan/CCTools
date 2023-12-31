import tkinter as tk
from PIL import Image, ImageTk

from cc_tools.cc2_sprite_set import CC2SpriteSet


class CC2SpritesetViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.image_label = None
        self.listbox = None
        self.configure(bg='black')  # Set the background color
        self.geometry("800x600")  # Set the window size to 800x600
        self.title("CC2 Sprite Viewer")

        # Sample dictionary mapping string keys to PIL images
        self.image_dict = CC2SpriteSet.factory("flat.bmp").sprites

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components."""
        list_frame = tk.Frame(self)
        list_frame.pack(side="left", fill="y")

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        for key in sorted(self.image_dict.keys()):
            self.listbox.insert(tk.END, key)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        self.image_label = tk.Label(self, bg="black")
        self.image_label.pack(side="right", fill="both", expand=True)

        self.listbox.bind("<<ListboxSelect>>", self.update_image)

    def update_image(self, event):
        """Update the image based on the selected key."""
        if not self.listbox.curselection():
            return  # Exit if no item is selected

        selected_key = self.listbox.get(self.listbox.curselection())
        pil_image = self.image_dict[selected_key]
        tk_image = ImageTk.PhotoImage(pil_image)
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image  # Keep a reference


# Run the application
if __name__ == "__main__":
    app = CC2SpritesetViewer()
    app.mainloop()
