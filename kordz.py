"""Kordz is a simple music player using tkinter."""

import os
import pygame
import tkinter as tk
from tkinter import ttk, Button, filedialog as fd
from random import randint
from PIL import Image, ImageTk


# pylint: disable="R0902, R0904"
class MusicPlayer(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        pygame.init()
        pygame.mixer.init()

        self.track_count: int = 0
        self.file_indices: int = 0

        self.song_list: list = []
        self.new_track_selection: list = []

        self.file_info: dict = {}
        self.icons: dict = {}

        self.is_music_paused: bool = False
        self.music_playing: bool = False
        self.is_mute: bool = False
        self.is_shuffle: bool = False
        self.is_playlist_repeat: bool = False
        self.is_track_repeat: bool = False

        self.menubar = None
        self.filemenu = None

        self.playlist_frame = None
        self.bottom_frame = None

        self.music_file = None
        self.song_directory = None

        self.shuffle_button = None
        self.previous_button = None
        self.play_button = None
        self.next_button = None
        self.repeat_button = None
        self.audio_button = None

        self.configure_window()
        self.setup_bottom_frame()

    def configure_window(self) -> None:
        # Add a title to the window
        self.title("Kordz Music Player")

        # Set the background color of the window
        self.configure(background="#212125")

        # Set the height and width of the window
        window_width: int = 1280
        window_height: int = 800

        # Set window geometry and center the window
        screen_width: int = self.winfo_screenwidth()
        screen_height: int = self.winfo_screenheight()
        x_coordinate: int = int((screen_width / 2) - (window_width / 2))
        y_coordinate: int = int((screen_height / 2.5) - (window_height / 2.5))
        self.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Make window not resizable
        self.resizable(0, 0)

        self.setup_menubar()

    def setup_menubar(self) -> None:
        # Create a main menu
        self.menubar = tk.Menu(self, tearoff=False)

        # Create file menu under main menu
        self.filemenu = tk.Menu(self.menubar, tearoff=False)

        # Add a separator above the menu
        self.filemenu.add_separator()

        # Add submenus under main menu
        self.filemenu.add_command(
            label="Open File...", font="Segoe 11", command=self.browse_file
        )
        self.filemenu.add_command(
            label="Open Folder...", font="Segoe 11", command=self.browse_directory
        )

        # Add a separator above the "Exit" command
        self.filemenu.add_separator()

        self.filemenu.add_command(label="Exit...", font="Segoe 11", command=exit)

        # Add file menu to main menu
        self.menubar.add_cascade(label="File", font="Segoe 11", menu=self.filemenu)

        # Configure main menu to root window
        self.config(menu=self.menubar)

    def setup_playlist_panel(self) -> None:
        # Create a frame for the playlist listbox
        self.playlist_frame = tk.Frame(self)
        self.playlist_frame.grid(row=0, column=0, sticky="w", padx=15)

        # Create a listbox for the playlist panel
        self.playlist_box = tk.Listbox(
            self.playlist_frame,
            bg="#111",
            fg="White",
            width=65,
            height=35,
            highlightthickness=0,
            relief=tk.FLAT,
        )
        self.playlist_box.grid(row=0, column=0)

        self.setup_scrollbar()

    def setup_scrollbar(self) -> None:
        # Create a vertical scrollbar for the playlist panel
        self.vertical_scrollbar = tk.Scrollbar(self.playlist_frame, orient=tk.VERTICAL)
        self.vertical_scrollbar.grid(row=0, column=1, sticky="ns")

        # Create a horizontal scrollbar for the playlist panel
        self.horizontal_scrollbar = tk.Scrollbar(
            self.playlist_frame, orient=tk.HORIZONTAL
        )
        self.horizontal_scrollbar.grid(row=1, column=0, sticky="we")

        # Attach the vertical and horizontal scrollbars to the listbox
        self.playlist_box.config(yscrollcommand=self.vertical_scrollbar.set)
        self.playlist_box.config(xscrollcommand=self.horizontal_scrollbar.set)

        # Set the listbox's scrollbar property to "yview"
        # for vertical and "xview" for horizontal
        self.vertical_scrollbar.config(command=self.playlist_box.yview)
        self.horizontal_scrollbar.config(command=self.playlist_box.xview)

    def load_icons(self) -> None:
        self.icons = {
            "shuffle_icon": ImageTk.PhotoImage(
                Image.open("./icons/shuffle.png").resize((30, 30))
            ),
            "previous_icon": ImageTk.PhotoImage(
                Image.open("./icons/previous.png").resize((30, 30))
            ),
            "next_icon": ImageTk.PhotoImage(
                Image.open("./icons/next.png").resize((30, 30))
            ),
            "play_pause_icon": (
                ImageTk.PhotoImage(Image.open("./icons/play.png").resize((30, 30))),
                ImageTk.PhotoImage(Image.open("./icons/pause.png").resize((30, 30))),
            ),
            "repeat_icon": (
                ImageTk.PhotoImage(Image.open("./icons/repeat.png").resize((30, 30))),
                ImageTk.PhotoImage(
                    Image.open("./icons/repeat_one.png").resize((30, 30))
                ),
            ),
            "volume_icon": (
                ImageTk.PhotoImage(Image.open("./icons/mute.png").resize((30, 30))),
                ImageTk.PhotoImage(
                    Image.open("./icons/low_volume.png").resize((30, 30))
                ),
                ImageTk.PhotoImage(
                    Image.open("./icons/medium_volume.png").resize((30, 30))
                ),
                ImageTk.PhotoImage(
                    Image.open("./icons/max_volume.png").resize((30, 30))
                ),
            ),
        }

    def setup_bottom_frame(self) -> None:
        self.bottom_frame = tk.Frame(bg="silver")
        self.bottom_frame.grid(row=1, column=0, sticky="ew")
        self.bottom_frame.grid_columnconfigure(6, minsize=50)
        self.bottom_frame.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.setup_buttons()

    def setup_buttons(self) -> None:
        self.load_icons()

        self.shuffle_button = Button(
            self.bottom_frame,
            relief=tk.FLAT,
            width=50,
            height=50,
            image=self.icons["shuffle_icon"],
            bg="silver",
            state=tk.DISABLED,
            highlightthickness=0,
            command=self.toggle_shuffle,
        )
        self.shuffle_button.grid(row=0, column=0, padx=67, pady=15)

        self.previous_button = Button(
            self.bottom_frame,
            relief=tk.FLAT,
            width=50,
            height=50,
            image=self.icons["previous_icon"],
            bg="silver",
            state=tk.DISABLED,
            highlightthickness=0,
            command=self.play_previous_track,
        )
        self.previous_button.grid(row=0, column=1, padx=67, pady=15)

        self.play_button = Button(
            self.bottom_frame,
            relief=tk.FLAT,
            width=50,
            height=50,
            image=self.icons["play_pause_icon"][0],
            bg="silver",
            state=tk.DISABLED,
            highlightthickness=0,
            command=self.toggle_play_pause,
        )
        self.play_button.grid(row=0, column=2, padx=67, pady=15)

        self.next_button = Button(
            self.bottom_frame,
            relief=tk.FLAT,
            width=50,
            height=50,
            image=self.icons["next_icon"],
            bg="silver",
            state=tk.DISABLED,
            highlightthickness=0,
            command=self.play_next_track,
        )
        self.next_button.grid(row=0, column=4, padx=67, pady=15)

        self.repeat_button = Button(
            self.bottom_frame,
            relief=tk.FLAT,
            width=50,
            height=50,
            image=self.icons["repeat_icon"][0],
            bg="silver",
            state=tk.DISABLED,
            highlightthickness=0,
            command=self.toggle_repeat,
        )
        self.repeat_button.grid(row=0, column=5, padx=67, pady=15)

        self.audio_button = Button(
            self.bottom_frame,
            relief=tk.FLAT,
            width=50,
            height=50,
            image=self.icons["volume_icon"][0],
            bg="silver",
            highlightthickness=0,
            command=self.toggle_mute_unmute,
        )
        self.audio_button.grid(row=0, column=8, pady=15)

        self.setup_volume_bar()

    def setup_volume_bar(self) -> None:
        self.volume_bar = ttk.Scale(
            self.bottom_frame,
            from_=0,
            to=1,
            orient=tk.HORIZONTAL,
            length=150,
            command=self.set_volume,
        )

        # Set the initial volume bar to 0.5
        self.volume_bar.set(0.5)
        # Grid the volume bar
        self.volume_bar.grid(row=0, column=9, padx=15)

    def browse_file(self) -> None:
        filetypes = [("Audio Files", ".mp3 .ogg .wav")]

        self.music_file: str = fd.askopenfilename(
            initialdir=os.getcwd(), title="Select A Song", filetypes=filetypes
        )

        if self.music_file:
            self.play_button.config(state=tk.NORMAL)
            self.repeat_button.config(state=tk.NORMAL)

        pygame.mixer.music.load(self.music_file)

    def browse_directory(self) -> None:
        self.song_directory: str = fd.askdirectory(
            initialdir=os.getcwd(), title="Select Directory With Songs"
        )

        if self.song_directory:
            self.setup_playlist_panel()
            self.shuffle_button.config(state=tk.NORMAL)
            self.previous_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
            self.play_button.config(state=tk.NORMAL)
            self.repeat_button.config(state=tk.NORMAL)

        self.load_directory_songs()

    def load_directory_songs(self) -> None:
        file_extension: tuple[str] = (
            "mp3",
            "wav",
            "ogg",
        )

        for file_index, song_filename in enumerate(os.listdir(self.song_directory)):
            song_path = os.path.join(self.song_directory, song_filename)
            if song_filename.endswith(file_extension):
                self.track_count += 1
                self.song_list.append(song_filename)
                self.playlist_box.insert(tk.END, f"{self.track_count}. {song_filename}")
                self.file_info[file_index] = [song_filename, song_path]

            self.file_indices += 1

    def start_music_playlist(self) -> None:
        self.track_info = self.file_info[self.playlist_box.curselection()[0]]
        self.play_button.config(image=self.icons["play_pause_icon"][1])
        pygame.mixer.music.load(self.track_info[1])
        pygame.mixer.music.play()

    def load_new_selection(self):
        self.track_info = self.new_track_selection
        pygame.mixer.music.load(self.track_info[1])
        pygame.mixer.music.play()

    def pause_music(self) -> None:
        if self.music_file or self.new_track_selection == self.track_info:
            pygame.mixer.music.pause()
            self.play_button.config(image=self.icons["play_pause_icon"][0])
            self.is_music_paused = True
        else:
            self.play_button.config(image=self.icons["play_pause_icon"][1])
            self.load_new_selection()

    def resume_music(self) -> None:
        if self.music_file or self.new_track_selection == self.track_info:
            pygame.mixer.music.unpause()
        else:
            self.load_new_selection()

        self.play_button.config(image=self.icons["play_pause_icon"][1])
        self.is_music_paused = False

    def check_music_state(self):
        self.new_track_selection = self.file_info[self.playlist_box.curselection()[0]]

        if self.is_music_paused:
            self.resume_music()
        elif not self.is_music_paused:
            self.pause_music()

    def play_music(self) -> None:
        if self.song_directory is not None:
            self.start_music_playlist()
        else:
            self.play_button.config(image=self.icons["play_pause_icon"][1])
            pygame.mixer.music.play()

        self.music_playing = True

    def toggle_play_pause(self) -> None:
        if not self.music_playing:
            self.play_music()
        else:
            self.check_music_state()

    def play_next_track(self) -> None:
        if self.is_shuffle:
            self.track_index = randint(0, self.playlist_box.size() - 1)
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.selection_set(self.track_index)
            self.playlist_box.activate(self.track_index)
            self.start_music_playlist()
        else:
            try:
                self.track_index = self.playlist_box.curselection()[0] + 1
                # Clear active bar in the playlist panel
                self.playlist_box.selection_clear(0, tk.END)
                # Set the active bar to the next song in the playlist
                self.playlist_box.selection_set(self.track_index)
                # Activate the new song bar
                self.playlist_box.activate(self.track_index)
                self.start_music_playlist()
            except IndexError:
                self.playlist_box.selection_set(0)
                self.playlist_box.activate(0)
                self.start_music_playlist()

    def play_previous_track(self):
        try:
            self.track_index = self.playlist_box.curselection()[0] - 1
            # Clear active bar in the playlist panel
            self.playlist_box.selection_clear(0, tk.END)
            # Set the active bar to the next song in the playlist
            self.playlist_box.selection_set(self.track_index)
            # Activate the new song bar
            self.playlist_box.activate(self.track_index)
            self.start_music_playlist()
        except IndexError:
            # Set the active bar to the last track in the playlist
            self.playlist_box.selection_set(tk.END)
            # Activate new selection bar for the last track in the playlist
            self.playlist_box.activate(tk.END)
            self.start_music_playlist()

    def check_event(self) -> None:
        # Variable to check whether or not current track has ended
        end_of_music = pygame.USEREVENT
        pygame.mixer.music.set_endevent(end_of_music)

        for event in pygame.event.get():
            if event.type == end_of_music:
                pygame.mixer.music.set_endevent(end_of_music)
                self.play_next_track()

        self.after(500, self.check_event)

    def set_volume(self, volume: str) -> None:
        self.sound_volume = float(volume)

        if self.sound_volume == 0.0:
            self.audio_button.config(image=self.icons["volume_icon"][0])
        elif 0.25 >= self.sound_volume <= 0.5:
            self.audio_button.config(image=self.icons["volume_icon"][1])
        elif 0.5 >= self.sound_volume <= 0.75:
            self.audio_button.config(image=self.icons["volume_icon"][2])
        else:
            self.audio_button.config(image=self.icons["volume_icon"][3])

        pygame.mixer.music.set_volume(self.sound_volume)

    def toggle_mute_unmute(self) -> None:
        if not self.is_mute:
            # Store the value of volume before muting
            self.previous_volume = self.sound_volume

            pygame.mixer.music.set_volume(0.0)
            self.volume_bar.set(0.0)
            self.audio_button.config(image=self.icons["volume_icon"][0])
            self.is_mute = True
        else:
            pygame.mixer.music.set_volume(self.previous_volume)
            # Set volume bar back to previous volume
            self.volume_bar.set(self.previous_volume)
            self.is_mute = False

    def toggle_shuffle(self) -> None:
        if self.is_shuffle:
            self.shuffle_button.config(relief=tk.FLAT, highlightthickness=0)
            self.is_shuffle = False
        else:
            self.shuffle_button.config(relief=tk.SUNKEN)
            self.is_shuffle = True

    def toggle_repeat(self) -> None:
        if self.is_playlist_repeat:
            self.repeat_button.config(
                relief=tk.SUNKEN, image=self.icons["repeat_icon"][1]
            )
            self.is_track_repeat = True
            self.is_playlist_repeat = False
        elif self.is_track_repeat:
            self.repeat_button.config(
                relief=tk.FLAT, image=self.icons["repeat_icon"][0]
            )
            self.is_playlist_repeat = False
            self.is_track_repeat = False
        else:
            self.repeat_button.config(relief=tk.SUNKEN)
            self.is_playlist_repeat = True


if __name__ == "__main__":
    MusicPlayer().mainloop()
