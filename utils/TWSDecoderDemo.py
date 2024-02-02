import tkinter as tk
from tkinter import filedialog, ttk

from cc_tools import TWSHandler
from cc_tools.tws_handler import TWSSolutionMoveDecoder


class TWSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.replay_set = None
        self.replay_number = 0
        self.title("TWS Decoder")
        self.geometry("800x600")

        self.menu_bar = tk.Menu(self)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open", command=self.load_file)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.config(menu=self.menu_bar)

        self.decoded_data = None

        # Setup a scrollable table for the decoded moves
        self.tree = ttk.Treeview(self, columns=(
            "Time", "Direction", "Format", "Bytes"), show="headings")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Direction", text="Direction")
        self.tree.heading("Format", text="Format")
        self.tree.heading("Bytes", text="Bytes")
        self.tree_scroll = ttk.Scrollbar(self, orient="vertical",
                                         command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree_scroll.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def load_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            handler = TWSHandler(file_path)
            self.replay_set = handler.decode()
            print(self.replay_set.header)
            print(self.replay_set.levelset_name)
            for fmt, count in self.replay_set.formats_seen.items():
                print(f"format {fmt}, count {count}")
            for replay in self.replay_set.replays:
                print(replay)
            self.replay_number = 0
            self.populate_tree()

    def populate_tree(self, event=None):
        print("*" * 80)
        self.tree.delete(
            *self.tree.get_children())  # Clear previous entries if any
        replay = self.replay_set.replays[self.replay_number]
        for move in replay.moves:
            self.tree.insert("", "end", values=(
                move.tick, move.direction, move.format,
                ' '.join(format(byte, '08b') for byte in move.bytes)))
            self.tree.yview_moveto(1)  # Auto-scroll to the bottom


if __name__ == "__main__":
    app = TWSApp()
    app.mainloop()
