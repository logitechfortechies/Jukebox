import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import pygame
from datetime import datetime
import os

class Track:
    def __init__(self, title, artist, filepath, album_cover=None, lyrics=None):
        self.title = title
        self.artist = artist
        self.filepath = filepath
        self.album_cover = album_cover
        self.lyrics = lyrics or "No lyrics available"
        self.duration = self.get_duration()

    def get_duration(self):
        """Return the duration of the track in seconds."""
        try:
            sound = pygame.mixer.Sound(self.filepath)
            return sound.get_length()
        except Exception as e:
            print(f"Error getting track duration: {e}")
            return 0

    def __str__(self):
        return f"{self.title} by {self.artist}"

class Jukebox:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Jukebox")
        self.root.geometry("600x800")

        self.tracks = []
        self.current_track = None
        self.current_time = 0

        pygame.mixer.init()

        # Track playing label
        self.track_label = ctk.CTkLabel(self.root, text="No track playing", font=("Arial", 14))
        self.track_label.pack(pady=10)

        # Track duration label
        self.track_duration_label = ctk.CTkLabel(self.root, text="Track Duration: --", font=("Arial", 12))
        self.track_duration_label.pack(pady=5)

        # Current time elapsed label
        self.current_time_label = ctk.CTkLabel(self.root, text="Current Time: --:--", font=("Arial", 12))
        self.current_time_label.pack(pady=5)

        # Album cover image label
        self.album_cover_label = ctk.CTkLabel(self.root, text="No Cover", font=("Arial", 12))
        self.album_cover_label.pack(pady=20)

        # Track listbox
        self.track_listbox = tk.Listbox(self.root, height=15, font=("Arial", 12))
        self.track_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.track_listbox.bind("<<ListboxSelect>>", self.select_track)

        # Buttons for adding, playing, stopping, and viewing lyrics
        self.add_track_button = ctk.CTkButton(self.root, text="Add Track", command=self.add_track)
        self.add_track_button.pack(pady=10)

        self.play_button = ctk.CTkButton(self.root, text="Play", command=self.play_track)
        self.play_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(self.root, text="Stop", command=self.stop_track)
        self.stop_button.pack(pady=10)

        self.lyrics_button = ctk.CTkButton(self.root, text="View Lyrics", command=self.view_lyrics)
        self.lyrics_button.pack(pady=10)

        # Timer for updating current time
        self.update_timer()

    def add_track(self):
        """Add a track to the library."""
        filepath = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3;*.wav")])
        if not filepath:
            return

        title = os.path.basename(filepath)
        album_cover = None  # You can enhance this by extracting cover art from the file
        lyrics = "Lyrics for this song..."
        
        track = Track(title=title, artist="Unknown", filepath=filepath, album_cover=album_cover, lyrics=lyrics)
        self.tracks.append(track)
        self.track_listbox.insert(tk.END, str(track))

    def select_track(self, event):
        """Handles track selection from the listbox."""
        selection = self.track_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_track = self.tracks[index]
            self.track_label.configure(text=f"Selected: {self.current_track}")
            self.update_duration()
            self.update_album_cover()

    def update_duration(self):
        """Updates the duration label when a track is selected."""
        if self.current_track:
            duration = self.current_track.duration
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            self.track_duration_label.configure(text=f"Track Duration: {minutes:02d}:{seconds:02d}")

    def update_album_cover(self):
        """Update the album cover image."""
        if self.current_track and self.current_track.album_cover:
            try:
                image = Image.open(self.current_track.album_cover)
                image = image.resize((200, 200))
                photo = ImageTk.PhotoImage(image)
                self.album_cover_label.configure(image=photo, text="")
                self.album_cover_label.image = photo
            except Exception as e:
                print(f"Error loading album cover: {e}")
        else:
            self.album_cover_label.configure(text="No Cover", image=None)

    def update_timer(self):
        """Update the current time of the track every second."""
        if self.current_track and pygame.mixer.music.get_busy():
            self.current_time += 1
            minutes = self.current_time // 60
            seconds = self.current_time % 60
            self.current_time_label.configure(text=f"Current Time: {minutes:02d}:{seconds:02d}")
        
        # Schedule the next update in 1 second
        self.root.after(1000, self.update_timer)

    def play_track(self):
        """Play the track selected from the listbox."""
        if not self.current_track:
            messagebox.showerror("Error", "No track selected.")
            return

        if not os.path.exists(self.current_track.filepath):
            messagebox.showerror("Error", f"File not found: {self.current_track.filepath}")
            return

        try:
            pygame.mixer.music.load(self.current_track.filepath)
            pygame.mixer.music.play()
            self.current_time = 0  # Reset current time on new track
            self.track_label.configure(text=f"Playing: {self.current_track}")
            self.update_album_cover()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play track: {e}")

    def stop_track(self):
        """Stop the track from playing."""
        pygame.mixer.music.stop()
        self.track_label.configure(text="No track playing")
        self.track_duration_label.configure(text="Track Duration: --")
        self.current_time_label.configure(text="Current Time: --:--")

    def view_lyrics(self):
        """Show the lyrics in a pop-up window."""
        if not self.current_track:
            messagebox.showerror("Error", "No track is currently playing.")
            return

        lyrics_window = ctk.CTkToplevel()
        lyrics_window.title(f"Lyrics - {self.current_track.title}")
        lyrics_text = ctk.CTkLabel(lyrics_window, text=self.current_track.lyrics, wraplength=400)
        lyrics_text.pack(padx=20, pady=20)

    def run(self):
        """Run the jukebox GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    jukebox = Jukebox()
    jukebox.run()
