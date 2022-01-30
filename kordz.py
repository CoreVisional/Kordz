"""Kordz is a simple music player using Tkinter & Pygame."""

import os
import tkinter as tk
from tkinter import Button, filedialog as fd
from tkinter import ttk
from PIL import Image, ImageTk
from pygame import mixer

# TODO: Implement shuffle and repeat features
# TODO: Implement a progress bar for active track
# TODO: Place a default album art when program first start
# TODO: Place an album art next to playlist. If only a file is selected, use default album art


class MusicPlayer(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        # Initialize pygame mixer
        mixer.init()

        self.is_music_paused = False
        self.music_playing = False
        self.is_on_repeat = False
        self.is_mute = False
        self.is_load_file = False

        self.previous_track_index = 0
        self.next_track_index = 0
        self.track_info = None

        self.song_directory = None

        self.song_list = []
        self.song_file_paths = []
        self.file_info = {}
        self.file_indices = 0

        self.configure_window()
        self.create_menubar()
        self.create_widgets()

    def configure_window(self):
        # Add a titlebar
        self.title("Korz Music Player")

        # Set background color
        self.configure(background="#212125")

        # Set the height and width of the window
        self.window_width = 1280
        self.window_height = 800

        # Set window geometry and center the window
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.x_coordinate = int((self.screen_width/2) - (self.window_width/2))
        self.y_coordinate = int((self.screen_height/2.5) - (self.window_height/2.5))
        self.geometry(
            f"{self.window_width}x{self.window_height}+{self.x_coordinate}+{self.y_coordinate}"
        )

        # Make window not resizable
        self.resizable(0, 0)

    def create_menubar(self):
        # Create a main menu
        self.menubar = tk.Menu(self, tearoff=False)

        # Create file menu under main menu
        self.filemenu = tk.Menu(self.menubar, tearoff=False)

        # Add a separator above the menu
        self.filemenu.add_separator()

        # Add submenus under main menu
        self.filemenu.add_command(
            label="Open...", font="Segoe 10", command=self.browse_file
        )
        self.filemenu.add_command(
            label="Open Folder...", font="Segoe 10", command=self.browse_directory
        )

        # Add a separator above the "Exit" command
        self.filemenu.add_separator()

        self.filemenu.add_command(label="Exit...", font="Segoe 10", command=exit)

        # Add file menu to main menu
        self.menubar.add_cascade(label="File", font="Segoe 10", menu=self.filemenu)

        # Configure main menu to root window
        self.config(menu=self.menubar)

    def create_widgets(self):
        self.create_bottom_frame()
        self.create_buttons()
        self.create_volume_slider()

    def create_bottom_frame(self):
        self.bottom_frame = tk.Frame(bg="silver")
        self.bottom_frame.grid(row=1, column=0, sticky="ew")
        self.bottom_frame.grid_columnconfigure(6, minsize=785)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def browse_directory(self):
        self.file_extension = ('mp3', 'wav', 'ogg',)
        self.song_directory = fd.askdirectory(initialdir=os.getcwd(), title="Select Directory With Songs")

        if self.song_directory:
            self.create_playlist_panel()
            self.shuffle_button.config(state=tk.NORMAL)
            self.previous_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
            self.play_button.config(state=tk.NORMAL)
            self.repeat_button.config(state=tk.NORMAL)

        self.load_songs()
        
    def load_songs(self):
        for file_index, song_filename in enumerate(os.listdir(self.song_directory)):
            song_path = os.path.join(self.song_directory, song_filename)
            if song_filename.endswith(self.file_extension):
                self.song_list.append(song_filename)
                self.playlist_box.insert(tk.END, song_filename)

                self.file_info[file_index] = [song_filename, song_path]

            self.file_indices += 1

    def browse_file(self):
        filetypes = [("Audio Files", ".mp3 .ogg .wav")]

        self.music_file = fd.askopenfilename(
            initialdir=os.getcwd(), title="Select A Song", filetypes=filetypes
        )

        if self.music_file:
            self.play_button.config(state=tk.NORMAL)
            self.repeat_button.config(state=tk.NORMAL)

        mixer.music.load(self.music_file)

    def load_icons(self):
        self.icons = {
            "shuffle_icon": ImageTk.PhotoImage(Image.open("icons/shuffle.png").resize((30, 30))),
            "previous_icon": ImageTk.PhotoImage(Image.open("icons/previous.png").resize((30, 30))),
            "next_icon": ImageTk.PhotoImage(Image.open("icons/next.png").resize((30, 30))),
            "play_pause_icon": (ImageTk.PhotoImage(Image.open("icons/play.png").resize((30, 30))),
                                ImageTk.PhotoImage(Image.open("icons/pause.png").resize((30, 30)))),
            "repeat_icon": (ImageTk.PhotoImage(Image.open("icons/repeat.png").resize((30, 30))),
                            ImageTk.PhotoImage(Image.open("icons/repeat_one.png").resize((30, 30)))),
            "volume_icon": (ImageTk.PhotoImage(Image.open("icons/mute.png").resize((30, 30))),
                            ImageTk.PhotoImage(Image.open("icons/low_volume.png").resize((30, 30))),
                            ImageTk.PhotoImage(Image.open("icons/medium_volume.png").resize((30, 30))),
                            ImageTk.PhotoImage(Image.open("icons/max_volume.png").resize((30, 30)))),
            }

    def create_buttons(self):
        self.load_icons()

        self.shuffle_button = Button(self.bottom_frame, relief=tk.FLAT, image=self.icons["shuffle_icon"], bg="silver", state=tk.DISABLED, highlightthickness=0, bd=0)
        self.shuffle_button.grid(row=0, column=0, padx=10)

        self.previous_button = Button(self.bottom_frame, relief=tk.FLAT, image=self.icons["previous_icon"], bg="silver", state=tk.DISABLED, highlightthickness=0, bd=0, command=self.play_previous_track)
        self.previous_button.grid(row=0, column=1, padx=10)

        self.play_button = Button(self.bottom_frame, relief=tk.FLAT, image=self.icons["play_pause_icon"][0], bg="silver", state=tk.DISABLED, highlightthickness=0, bd=0, command=self.toggle_play_pause)
        self.play_button.grid(row=0, column=2, padx=10)

        self.next_button = Button(self.bottom_frame, relief=tk.FLAT, image=self.icons["next_icon"], bg="silver", state=tk.DISABLED, highlightthickness=0, bd=0, command=self.play_next_song)
        self.next_button.grid(row=0, column=4, padx=10)

        self.repeat_button = Button(self.bottom_frame, relief=tk.FLAT, image=self.icons["repeat_icon"][0], bg="silver", state=tk.DISABLED, highlightthickness=0, bd=0)
        self.repeat_button.grid(row=0, column=5, padx=10)

        self.audio_mute_button = Button(self.bottom_frame, relief=tk.FLAT, image=self.icons["volume_icon"][0], bg="silver", highlightthickness=0, bd=0, command=self.toggle_mute_unmute)
        self.audio_mute_button.grid(row=0, column=8, padx=10)

    def create_playlist_panel(self):
        # Create a frame for the playlist listbox
        self.playlist_frame = tk.Frame(self)
        self.playlist_frame.grid(row=0, column=0, sticky="w", padx=15)
    
        # Create a listbox for the playlist panel
        self.playlist_box = tk.Listbox(self.playlist_frame, bg="#111", fg="White", width=60, height=45, highlightthickness=0, relief=tk.FLAT)
        self.playlist_box.grid(row=0, column=0)

        # Create a vertical scrollbar for the playlist panel
        self.vertical_scrollbar = tk.Scrollbar(self.playlist_frame, orient=tk.VERTICAL)
        self.vertical_scrollbar.grid(row=0, column=1, sticky="ns")

        # Create a horizontal scrollbar for the playlist panel
        self.horizontal_scrollbar = tk.Scrollbar(self.playlist_frame, orient=tk.HORIZONTAL)
        self.horizontal_scrollbar.grid(row=1, column=0, sticky="we")

        # Attach the vertical and horizontal scrollbars to the listbox
        self.playlist_box.config(yscrollcommand=self.vertical_scrollbar.set)
        self.playlist_box.config(xscrollcommand=self.horizontal_scrollbar.set)

        # Set the listbox's scrollbar property to "yview" for vertical and "xview" for horizontal
        self.vertical_scrollbar.config(command=self.playlist_box.yview)
        self.horizontal_scrollbar.config(command=self.playlist_box.xview)
    
    def start_music_playlist(self):
        self.track_info = self.file_info[self.playlist_box.curselection()[0]]
        mixer.music.load(self.track_info[1])
        mixer.music.play()

    def play_previous_track(self):
        try:
            self.previous_track_index = self.playlist_box.curselection()[0] - 1

            # Clear active bar in the playlist panel
            self.playlist_box.selection_clear(0, tk.END)

            # Set the active bar to the next song in the playlist
            self.playlist_box.selection_set(self.previous_track_index)

            # Activate the new song bar
            self.playlist_box.activate(self.previous_track_index)

            self.start_music_playlist()
        except IndexError:
            # Set the active bar to the last track in the playlist
            self.playlist_box.selection_set(tk.END)
            # Activate new selection bar for the last track in the playlist
            self.playlist_box.activate(tk.END)

            self.start_music_playlist()
    
    def play_next_song(self):
        try:
            self.next_track_index = self.playlist_box.curselection()[0] + 1

            # Clear active bar in the playlist panel
            self.playlist_box.selection_clear(0, tk.END)

            # Set the active bar to the next song in the playlist
            self.playlist_box.selection_set(self.next_track_index)

            # Activate the new song bar
            self.playlist_box.activate(self.next_track_index)

            self.start_music_playlist()
        except IndexError:
            self.playlist_box.selection_set(0)
            self.playlist_box.activate(0)
            self.start_music_playlist()

    def play_music(self):
        if self.song_directory is not None:
            self.start_music_playlist()
        else:
            mixer.music.play()

        self.play_button.config(image=self.icons["play_pause_icon"][1])
        self.music_playing = True

    def pause_music(self):
        mixer.music.pause()
        self.play_button.config(image=self.icons["play_pause_icon"][0])
        self.is_music_paused = True

    def unpause_music(self):
        mixer.music.unpause()
        self.play_button.config(image=self.icons["play_pause_icon"][1])
        self.is_music_paused = False

    def toggle_play_pause(self):
        if not self.music_playing:
            self.play_music()
        else:
            if self.is_music_paused:
                self.unpause_music()
            elif not self.is_music_paused:
                self.pause_music()
    
    def set_volume(self, volume):
        self.sound_volume = float(volume)

        if self.sound_volume == 0.0:
            self.audio_mute_button.config(image=self.icons["volume_icon"][0])
        elif 0.25 >= self.sound_volume <= 0.5:
            self.audio_mute_button.config(image=self.icons["volume_icon"][1])
        elif 0.5 >= self.sound_volume <= 0.75:
            self.audio_mute_button.config(image=self.icons["volume_icon"][2])
        else:
            self.audio_mute_button.config(image=self.icons["volume_icon"][3])

        mixer.music.set_volume(self.sound_volume)

    def create_volume_slider(self):
        self.volume_bar = ttk.Scale(
            self.bottom_frame,
            from_=0, to=1,
            orient=tk.HORIZONTAL,
            length=150,
            command=self.set_volume
            )
        
        # Set the initial volume bar to 0.5
        self.volume_bar.set(0.5)

        # Grid the volume bar
        self.volume_bar.grid(row=0, column=9, padx=10)

    def toggle_mute_unmute(self):
        if not self.is_mute:
            mixer.music.set_volume(0)
            self.audio_mute_button.config(image=self.icons["volume_icon"][0])
            self.is_mute = True
        else:
            self.set_volume(self.sound_volume)
            self.is_mute = False

if __name__ == "__main__":
    root = MusicPlayer()
    root.mainloop()
