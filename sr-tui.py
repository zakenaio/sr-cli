#!/usr/bin/env python3
import requests
import sys
import argparse
import subprocess
import time
import threading
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.align import Align
import json
import socket
import select
import tty
import termios
import os
import logging
import re
from datetime import datetime
import unicodedata

# Configure logging
logging.basicConfig(
    filename=f"/tmp/sr-tui-debug-{os.getuid()}.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Base URL for SR API
BASE_URL = "https://api.sr.se/api/v2"

# Dynamic MPV socket path to avoid permission issues between users
MPV_SOCKET_PATH = f"/tmp/sr-tui-mpv-{os.getuid()}.sock"

# Spotify-inspired colors
SPOTIFY_GREEN = "#1DB954"
LIGHT_TEXT = "#FFFFFF"
GRAY_TEXT = "#B3B3B3"

# ASCII Block Font for "Big Text" (3x5)
BIG_FONT = {
    'A': ["▄▀▄", "█ █", "█▀█", "█ █", "█ █"],
    'B': ["█▀▀▄", "█▄▄▀", "█  █", "█  █", "█▄▄▀"],
    'C': ["▄▀▀ ", "█   ", "█   ", "█   ", " ▀▀ "],
    'D': ["█▀▀▄", "█  █", "█  █", "█  █", "█▄▄▀"],
    'E': ["█▀▀", "█  ", "█▀▀", "█  ", "█▄▄"],
    'F': ["█▀▀▀", "█▀▀ ", "█▀▀ ", "█  ", "▀   "],
    'G': ["▄▀▀ ", "█   ", "█ ▄▄", "█  █", "▀▄▄▀"],
    'H': ["█  █", "█  █", "█▀▀█", "█  █", "█  █"],
    'I': ["▀█▀", " █ ", " █ ", " █ ", "▄█▄"],
    'J': ["   █", "   █", "   █", "▄  █", " ▀▄▀"],
    'K': ["█  █", "█ ▄▀", "█▀▄ ", "█  █", "█  █"],
    'L': ["█  ", "█  ", "█  ", "█  ", "█▄▄"],
    'M': ["█   █", "█▄ ▄█", "█ ▀ █", "█   █", "█   █"],
    'N': ["█   █", "██  █", "█ █ █", "█  ██", "█   █"],
    'O': ["▄▀▀▄", "█  █", "█  █", "█  █", "▀▄▄▀"],
    'P': ["█▀▀▄", "█▄▄▀", "█   ", "█   ", "█   "],
    'Q': ["▄▀▀▄", "█  █", "█  █", "█  █", " ▀▄▀▄"],
    'R': ["█▀▀▄", "█▄▄▀", "█  █", "█  █", "█  █"],
    'S': ["▄▀▀ ", "█   ", "▀▄▄▄", "   █", "▄▄▄▀"],
    'T': ["▀█▀", " █ ", " █ ", " █ ", " █ "],
    'U': ["█ █", "█ █", "█ █", "█ █", "▀▄▀"],
    'V': ["█ █", "█ █", "█ █", "▀▄▀", "  █  "],
    'W': ["█   █", "█   █", "█ ▄ █", "██▄██", "█   █"],
    'X': ["█ █", "▀▄▀", " █ ", "▄▀▄", "█ █"],
    'Y': ["█ █", "▀▄▀", " █ ", " █ ", " █ "],
    'Z': ["▀▀▀█", "  █ ", " █  ", "█   ", "▀▀▀▀"],
    'Å': [" ▀ ", "█▀█", "█▀█", "█ █", "█ █"],
    'Ä': ["▀ ▀", "█▀█", "█▀█", "█ █", "█ █"],
    'Ö': ["▀  ▀", "▄▀▀▄", "█  █", "█  █", "▀▄▄▀"],
    'Á': [" ▀ ", "█▀█", "█▀█", "█ █", "█ █"],
    '0': [" ▄▀▀▄ ", "█  █ █", "█ █  █", "█    █", " ▀▄▄▀ "],
    '1': [" ▄█ ", "  █ ", "  █ ", "  █ ", " ▄█▄"],
    '2': [" ▄▀▀▄ ", "    █", "  ▄▀ ", " █   ", " ▀▀▀▀"],
    '3': [" ▀▀▀▄ ", "    █", "  ▀▀▄", "    █", " ▄▄▄▀"],
    '4': ["█  █", "█  █", "▀▀▀█", "   █", "   █"],
    '5': ["█▀▀▀▀", "█▀▀▀ ", " ▀▀▀▄", "    █", "▀▀▀▀ "],
    '6': [" ▄▀▀▀", "█▀▀▀▄", "█   █", "▀▄▄▄▀", " ▀▀▀ "],
    '7': ["▀▀▀▀█", "   █ ", "  █  ", " █   ", " █   "],
    '8': [" ▄▀▀▄ ", "█▄▄▄█", " ▄▀▀▄ ", "█▄▄▄█", " ▀▄▄▀ "],
    '9': [" ▄▀▀▄ ", "█▄▄▄█", " ▀▀▀█", "    █", " ▀▀▀ "],
    ' ': ["     ", "     ", "     ", "     ", "     "],
    ':': ["   ", " ▄ ", "   ", " ▄ ", "   "],
    '-': ["     ", "     ", "▀▀▀▀▀", "     ", "     "],
    '.': ["   ", "   ", "   ", "   ", " ▄ "],
    '♪': ["  ▄▀", " █  ", " █  ", " ▀▄ ", "   ▀"],
    '?': [" ▄▀▀▄ ", "    █", "  ▄▀ ", "     ", "  ▄  "],
}

console = Console()

class SRPlayer:
    def __init__(self):
        # Mode: 'radio' or 'podcast'
        self.mode = 'radio'
        
        # Radio mode state
        self.channels = []
        self.selected_index = 0
        self.playing_channel = None
        
        # Podcast mode state
        self.podcasts = []
        self.selected_podcast_index = 0
        self.episodes = []
        self.selected_episode_index = 0
        self.playing_episode = None
        self.active_podcast_pane = 'programs'  # 'programs' or 'episodes'
        
        # Playback state
        self.mpv_process = None
        self.running = True
        self.current_program = "Loading..."
        self.current_song = ""
        self.filter_text = ""
        self.is_playing = False
        self.last_metadata_fetch = 0
        self.metadata_fetch_interval = 10
        
        # Search mode state
        self.search_mode = False
        self.search_buffer = ""
        
        # Podcast playback tracking
        self.current_position = 0.0  # seconds
        self.total_duration = 0.0    # seconds
        self.is_podcast_playing = False
        
    def render_big_text(self, text, color=SPOTIFY_GREEN):
        """Converts text to ASCII block letters."""
        text = unicodedata.normalize('NFC', text).upper()
        lines = ["", "", "", "", ""]
        
        for char in text:
            char_lines = BIG_FONT.get(char, BIG_FONT.get('?', ["   "]*5))
            for i in range(5):
                lines[i] += char_lines[i] + "  "
        
        result = Text()
        for line in lines:
            result.append(line.rstrip() + "\n", style=color)
        return result
        
    def get_channels(self):
        """Fetches the list of channels from the SR API."""
        try:
            response = requests.get(f"{BASE_URL}/channels?format=json&pagination=false")
            response.raise_for_status()
            data = response.json()
            
            if 'channels' in data:
                self.channels = data['channels']
                return True
        except Exception as e:
            console.print(f"[red]Error fetching channels: {e}[/red]")
            return False
        return False
    
    def get_live_url(self, channel_id):
        """Fetches the live audio URL for a channel."""
        try:
            url = f"{BASE_URL}/channels/{channel_id}?format=json"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if 'channel' in data and 'liveaudio' in data['channel']:
                return data['channel']['liveaudio']['url']
        except Exception:
            pass
        return None
    
    def get_now_playing(self, channel_id):
        """Fetches current program and song metadata."""
        program_title = "Unknown Program"
        song_title = ""
        
        # Get scheduled episode
        try:
            prog_url = f"{BASE_URL}/scheduledepisodes/rightnow?channelid={channel_id}&format=json"
            response = requests.get(prog_url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                if 'channel' in data and 'currentscheduledepisode' in data['channel']:
                    program_title = data['channel']['currentscheduledepisode'].get('title', 'Unknown Program')
        except Exception:
            pass

        # Get current song
        try:
            song_url = f"{BASE_URL}/playlists/rightnow?channelid={channel_id}&format=json"
            response = requests.get(song_url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                if 'playlist' in data and 'song' in data['playlist']:
                    song = data['playlist']['song']
                    if 'description' in song:
                        song_title = song['description']
                    elif 'artist' in song and 'title' in song:
                        song_title = f"{song['artist']} - {song['title']}"
        except Exception:
            pass
            
        return program_title, song_title
    
    def update_metadata(self):
        """Updates metadata in background thread."""
        while self.running:
            if self.is_playing and self.mode == 'radio':
                current_time = time.time()
                if current_time - self.last_metadata_fetch > self.metadata_fetch_interval:
                    if self.playing_channel:
                        self.current_program, self.current_song = self.get_now_playing(
                            self.playing_channel['id']
                        )
                        self.last_metadata_fetch = current_time
            time.sleep(1)
    
    def get_podcasts(self):
        """Fetches the list of podcast programs from the SR API."""
        try:
            response = requests.get(f"{BASE_URL}/programs/index?haspod=true&format=json&pagination=false")
            response.raise_for_status()
            data = response.json()
            
            if 'programs' in data:
                self.podcasts = data['programs']
                return True
        except Exception as e:
            console.print(f"[red]Error fetching podcasts: {e}[/red]")
            return False
        return False
    
    def get_episodes(self, program_id):
        """Fetches episodes for a specific podcast program using the episodes endpoint for richer metadata."""
        try:
            # Use episodes endpoint instead of podfiles for better descriptions and titles
            response = requests.get(f"{BASE_URL}/episodes/index?programid={program_id}&format=json&pagination=false")
            response.raise_for_status()
            data = response.json()
            
            if 'episodes' in data:
                # Map episodes to a consistent format
                self.episodes = []
                for ep in data['episodes']:
                    # Extract stream URL from listenpodfile or fallback
                    url = ""
                    duration = 0
                    if 'listenpodfile' in ep:
                        url = ep['listenpodfile'].get('url', '')
                        duration = ep['listenpodfile'].get('duration', 0)
                    
                    # Parse publish date
                    date_str = ""
                    publish_date = ep.get('publishdateutc', '')
                    date_match = re.search(r'(\d+)', publish_date)
                    if date_match:
                        ts = int(date_match.group(1)) / 1000.0
                        date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
                    
                    self.episodes.append({
                        'id': ep.get('id'),
                        'title': ep.get('title', 'Unknown Episode'),
                        'description': ep.get('description', ''),
                        'url': url,
                        'duration': duration,
                        'program': ep.get('program', {}),
                        'date': date_str
                    })
                return True
        except Exception as e:
            console.print(f"[red]Error fetching episodes: {e}[/red]")
            return False
        return False
    
    def format_time(self, seconds):
        """Formats seconds to MM:SS or HH:MM:SS."""
        if seconds < 0:
            seconds = 0
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    def get_playback_position(self):
        """Gets current playback position from mpv via IPC."""
        if not self.is_podcast_playing or not self.mpv_process:
            return 0.0
        
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect(MPV_SOCKET_PATH)
            
            # Request time-pos
            command = json.dumps({"command": ["get_property", "time-pos"]}) + "\n"
            sock.send(command.encode())
            
            response = sock.recv(4096).decode()
            sock.close()
            
            data = json.loads(response)
            if 'data' in data and data['data'] is not None:
                return float(data['data'])
        except:
            pass
        
        return self.current_position
    
    def seek(self, seconds):
        """Seeks forward or backward by specified seconds."""
        if not self.mpv_process or self.mpv_process.poll() is not None:
            return
        
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect(MPV_SOCKET_PATH)
            
            command = json.dumps({"command": ["seek", seconds, "relative"]}) + "\n"
            sock.send(command.encode())
            sock.close()
            
            # Update position estimate
            self.current_position += seconds
            if self.current_position < 0:
                self.current_position = 0
            if self.current_position > self.total_duration:
                self.current_position = self.total_duration
        except:
            pass
    
    def toggle_mode(self):
        """Toggles between radio and podcast mode."""
        if self.mode == 'radio':
            self.mode = 'podcast'
            # Fetch podcasts if not already loaded
            if not self.podcasts:
                self.get_podcasts()
        else:
            self.mode = 'radio'
            self.active_podcast_pane = 'programs'
    
    def update_podcast_position(self):
        """Updates podcast playback position in background thread."""
        while self.running:
            if self.is_podcast_playing:
                self.current_position = self.get_playback_position()
            time.sleep(1)
    
    def play_channel(self, channel):
        """Starts or switches to a channel."""
        # Stop current playback
        if self.mpv_process and self.mpv_process.poll() is None:
            self.mpv_process.terminate()
            self.mpv_process.wait()
        
        # Get stream URL
        url = self.get_live_url(channel['id'])
        if not url:
            self.current_program = "Error: Could not get stream URL"
            self.current_song = ""
            self.is_playing = False
            return
        
        # Start mpv
        try:
            self.mpv_process = subprocess.Popen(
                ["mpv", "--no-video", "--quiet", f"--input-ipc-server={MPV_SOCKET_PATH}", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.playing_channel = channel
            self.is_playing = True
            self.is_podcast_playing = False
            self.current_program = "Loading..."
            self.current_song = ""
            
            # Fetch metadata immediately in a thread to avoid blocking
            def fetch_initial_metadata():
                time.sleep(0.5)  # Give stream time to start
                prog, song = self.get_now_playing(channel['id'])
                self.current_program = prog
                self.current_song = song
                self.last_metadata_fetch = time.time()
            
            threading.Thread(target=fetch_initial_metadata, daemon=True).start()
            
        except FileNotFoundError:
            self.current_program = "Error: mpv not installed"
            self.current_song = "Please install mpv to play audio"
            self.is_playing = False
    
    def toggle_pause(self):
        """Toggles pause/resume of playback."""
        if self.mpv_process and self.mpv_process.poll() is None:
            try:
                # Send pause command to mpv via IPC
                import socket
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(MPV_SOCKET_PATH)
                sock.send(b'{"command": ["cycle", "pause"]}\n')
                sock.close()
                self.is_playing = not self.is_playing
            except:
                pass
    
    def play_episode(self, episode):
        """Plays a podcast episode."""
        # Stop current playback
        if self.mpv_process and self.mpv_process.poll() is None:
            self.mpv_process.terminate()
            self.mpv_process.wait()
        
        # Get episode URL
        url = episode.get('url')
        if not url:
            return
        
        # Start mpv
        try:
            self.mpv_process = subprocess.Popen(
                ["mpv", "--no-video", "--quiet", f"--input-ipc-server={MPV_SOCKET_PATH}", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.playing_episode = episode
            self.is_playing = True
            self.is_podcast_playing = True
            self.current_position = 0.0
            self.total_duration = float(episode.get('duration', 0))
            
            # Restart or ensure position tracking thread is active
            # (In this simple structure, the thread runs while self.running is true)
            
        except FileNotFoundError:
            console.print("[red]Error: mpv not installed[/red]")
            self.is_playing = False
            self.is_podcast_playing = False
    
    def get_filtered_channels(self):
        """Returns channels filtered by search text."""
        if not self.filter_text:
            return self.channels
        
        filter_lower = self.filter_text.lower()
        return [ch for ch in self.channels if filter_lower in ch['name'].lower()]
    
    def get_filtered_podcasts(self):
        """Returns podcasts filtered by search text."""
        if not self.filter_text:
            return self.podcasts
        
        filter_lower = self.filter_text.lower()
        return [p for p in self.podcasts if filter_lower in p.get('name', '').lower()]
    
    def get_filtered_episodes(self):
        """Returns episodes filtered by search text."""
        if not self.filter_text:
            return self.episodes
        
        filter_lower = self.filter_text.lower()
        return [e for e in self.episodes if filter_lower in e.get('title', '').lower()]
    
    def create_channel_list(self):
        """Creates the channel list panel."""
        filtered = self.get_filtered_channels()
        
        table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        table.add_column("Channel", style=GRAY_TEXT)
        
        # Adjust selected index if filter changed
        if self.selected_index >= len(filtered):
            self.selected_index = max(0, len(filtered) - 1)
            
        # Dynamic scroll window based on terminal height
        # We use a larger buffer to ensure it fills the space
        terminal_height = console.size.height
        window_size = max(20, terminal_height - 8)
        
        start_idx = max(0, self.selected_index - window_size // 2)
        end_idx = min(len(filtered), start_idx + window_size)
        
        for i, channel in enumerate(filtered[start_idx:end_idx]):
            actual_index = start_idx + i
            is_selected = actual_index == self.selected_index
            is_playing = self.playing_channel and channel['id'] == self.playing_channel['id']
            
            prefix = "▶ " if is_playing else "  "
            name = channel['name']
            
            if is_selected:
                style = f"bold {SPOTIFY_GREEN}"
                text = Text(f"{prefix}{name}", style=style)
            else:
                text = Text(f"{prefix}{name}")
            
            table.add_row(text)
        
        # Create title with search indicator
        title = "Channels"
        if self.filter_text:
            title += f" (filter: {self.filter_text})"
        
        return Panel(
            table,
            title=title,
            border_style=SPOTIFY_GREEN,
            padding=(1, 2)
        )
    
    def create_podcast_list(self):
        """Creates the podcast programs list panel."""
        filtered = self.get_filtered_podcasts()
        
        table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        table.add_column("Podcast", style=GRAY_TEXT)
        
        # Adjust selected index if filter changed
        if self.selected_podcast_index >= len(filtered):
            self.selected_podcast_index = max(0, len(filtered) - 1)
        
        # Dynamic scroll window based on terminal height
        terminal_height = console.size.height
        window_size = max(20, terminal_height - 8)
        
        start_idx = max(0, self.selected_podcast_index - window_size // 2)
        end_idx = min(len(filtered), start_idx + window_size)
        
        for i, podcast in enumerate(filtered[start_idx:end_idx]):
            actual_index = start_idx + i
            is_selected = actual_index == self.selected_podcast_index
            name = podcast.get('name', 'Unknown')
            
            if is_selected:
                text = Text(f"  {name}", style=f"bold {SPOTIFY_GREEN}")
            else:
                text = Text(f"  {name}")
            
            table.add_row(text)
        
        title = "Podcasts"
        if self.filter_text:
            title += f" (filter: {self.filter_text})"
            
        border_color = SPOTIFY_GREEN if self.active_podcast_pane == 'programs' else "white"
        
        return Panel(table, title=title, border_style=border_color, padding=(1, 2))
    
    def create_episode_list(self):
        """Creates the episode list panel."""
        if not self.episodes:
            content = Align.center(
                Text("\nSelect a podcast & press Enter\n", style=GRAY_TEXT),
                vertical="middle"
            )
            border_color = SPOTIFY_GREEN if self.active_podcast_pane == 'episodes' else "dim white"
            return Panel(content, title="Episodes", border_style=border_color, padding=(1, 2))
        
        filtered = self.get_filtered_episodes()
        
        table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        table.add_column("Episode", style=GRAY_TEXT)
        
        # Adjust selected index if filter changed
        if self.selected_episode_index >= len(filtered):
            self.selected_episode_index = max(0, len(filtered) - 1)
        
        # Dynamic scroll window
        terminal_height = console.size.height
        window_size = max(20, terminal_height - 8)
        
        start_idx = max(0, self.selected_episode_index - window_size // 2)
        end_idx = min(len(filtered), start_idx + window_size)
        
        for i, episode in enumerate(filtered[start_idx:end_idx]):
            actual_index = start_idx + i
            is_selected = actual_index == self.selected_episode_index
            is_playing = self.playing_episode and episode.get('id') == self.playing_episode.get('id')
            
            # Format title for list: use date + first part of title if possible
            display_title = episode.get('date', 'Unknown Date')
            # If we want a bit of the title too:
            # title = episode.get('title', 'Unknown')
            # display_title = f"{episode.get('date')} - {title}"
            
            if len(display_title) > 60:
                display_title = display_title[:57] + "..."
            duration = self.format_time(episode.get('duration', 0))
            prefix = "▶ " if is_playing else "  "
            display = f"{prefix}{display_title} [{duration}]"
            
            if is_selected:
                text = Text(display, style=f"bold {SPOTIFY_GREEN}")
            else:
                text = Text(display)
            
            table.add_row(text)
        
        title = "Episodes"
        if self.filter_text:
            title += f" (filter: {self.filter_text})"
            
        border_color = SPOTIFY_GREEN if self.active_podcast_pane == 'episodes' else "white"
        
        return Panel(table, title=title, border_style=border_color, padding=(1, 2))
    
    def create_progress_bar(self):
        """Creates progress bar for podcast playback."""
        if not self.is_podcast_playing or not self.playing_episode:
            return Text("")
        
        # Calculate progress percentage
        progress = 0.0
        if self.total_duration > 0:
            progress = (self.current_position / self.total_duration) * 100
        
        # Create progress bar
        bar_width = 40
        filled = int((progress / 100) * bar_width)
        bar = "━" * filled + "─" * (bar_width - filled)
        
        current_time_str = self.format_time(self.current_position)
        total_time_str = self.format_time(self.total_duration)
        
        progress_text = Text()
        progress_text.append(f"{current_time_str} ", style=GRAY_TEXT)
        progress_text.append(bar, style=SPOTIFY_GREEN)
        progress_text.append(f" {total_time_str}", style=GRAY_TEXT)
        
        return progress_text
    
    def create_now_playing(self):
        """Creates the now playing panel with responsive sizing."""
        # Get terminal size for responsive layout
        terminal_height = console.size.height
        terminal_width = console.size.width
        is_tiny = terminal_height < 15
        is_large = terminal_height > 30
        is_huge = terminal_height > 50

        # Podcast mode
        if self.mode == 'podcast' and self.playing_episode:
            title = self.playing_episode.get('title', 'Unknown Episode')
            program = self.playing_episode.get('program', {})
            program_name = program.get('name', 'Unknown') if isinstance(program, dict) else 'Unknown'
            status = "▶ Playing" if self.is_playing else "⏸ Paused"
            
            if is_tiny:
                # Compact single-line layout for tiny windows
                content = Text.assemble(
                    (f"{status} ", SPOTIFY_GREEN),
                    (f"{title} ", f"bold {LIGHT_TEXT}"),
                    (f"({program_name})", GRAY_TEXT)
                )
                return Panel(Align.center(content, vertical="middle"), title="Now Playing", border_style=SPOTIFY_GREEN)

            # Retrieve description with fallback to program description
            description = self.playing_episode.get('description', '')
            if not description and isinstance(program, dict):
                description = program.get('description', '')

            # Use precise spacing for podcast mode
            pod_spacing = "\n"
            
            lines = []
            if is_large:
                available_width = (terminal_width // 2) - 10
                if len(program_name) * 5 <= available_width:
                    lines.append(self.render_big_text(program_name))
                else:
                    lines.append(Text(program_name, style=f"bold {LIGHT_TEXT} underline"))
                lines.append(Text(""))
            else:
                lines.append(Text(program_name, style=f"bold {LIGHT_TEXT} underline"))
                lines.append(Text(""))
            
            lines.append(Text("Episode", style=GRAY_TEXT))
            lines.append(Text(title, style=f"bold {LIGHT_TEXT}"))
            
            if is_large:
                lines.append(Text(""))
            
            progress_bar = self.create_progress_bar()
            if progress_bar:
                lines.append(progress_bar)
                if is_large:
                    lines.append(Text(""))
            
            lines.append(Text(status, style=f"bold {SPOTIFY_GREEN}"))
            
            if description:
                # Add description at the very bottom with wrapping
                lines.append(Text(""))
                desc_text = Text(description, style=GRAY_TEXT)
                # Simple word wrap logic for description
                lines.append(desc_text)
            
            content = Align.center(Text("\n").join([line for line in lines if line is not None]), vertical="middle")
        
        # Radio mode
        elif self.mode == 'radio' and self.playing_channel:
            channel_name = self.playing_channel['name']
            status = "▶ Playing" if self.is_playing else "Paused"
            
            if is_tiny:
                # Compact single-line layout for tiny windows
                content = Text.assemble(
                    (f"{status} ", SPOTIFY_GREEN),
                    (f"{channel_name}: ", f"bold {LIGHT_TEXT}"),
                    (f"{self.current_program}", LIGHT_TEXT)
                )
                if self.current_song:
                    content.append(f" ♪ {self.current_song}", style=SPOTIFY_GREEN)
                return Panel(Align.center(content, vertical="middle"), title="🎵 Now Playing", border_style=SPOTIFY_GREEN)

            lines = []
            if is_large:
                available_width = (terminal_width * 2 // 3) - 10
                if len(channel_name) * 5 <= available_width:
                    lines.append(self.render_big_text(channel_name))
                else:
                    lines.append(Text(channel_name, style=f"bold {LIGHT_TEXT} underline"))
                lines.append(Text(""))
            else:
                lines.append(Text(channel_name, style=f"bold {LIGHT_TEXT} underline"))
                lines.append(Text(""))
            
            lines.append(Text("Program", style=GRAY_TEXT))
            lines.append(Text(self.current_program, style=f"bold {LIGHT_TEXT}"))
            
            if self.current_song:
                if is_large:
                    lines.append(Text(""))
                lines.append(Text("♪ Now Playing", style=GRAY_TEXT))
                lines.append(Text(self.current_song, style=f"bold {SPOTIFY_GREEN}"))
            
            if is_large:
                lines.append(Text(""))
            
            lines.append(Text(status, style=f"bold {SPOTIFY_GREEN}"))
            
            content = Align.center(Text("\n").join([line for line in lines if line is not None]), vertical="middle")
        
        else:
            msg = "♪  Select a channel" if self.mode == 'radio' else "Select a podcast"
            content = Align.center(Text(f"\n{msg}\n", style=GRAY_TEXT), vertical="middle")
        
        return Panel(content, title="Now Playing", border_style=SPOTIFY_GREEN, padding=(2, 4))
    
    def create_search_panel(self):
        """Creates the search input panel."""
        if not self.search_mode:
            return None
        
        # Create search text with cursor
        search_text = Text()
        search_text.append("🔍 ", style=SPOTIFY_GREEN)
        search_text.append(self.search_buffer, style=LIGHT_TEXT)
        search_text.append("█", style=f"bold {SPOTIFY_GREEN}")  # Cursor
        
        # Instructions
        instructions = Text()
        instructions.append("  ", style=GRAY_TEXT)
        instructions.append("Enter", style=f"bold {SPOTIFY_GREEN}")
        instructions.append(" to apply  ", style=GRAY_TEXT)
        instructions.append("Esc", style=f"bold {SPOTIFY_GREEN}")
        instructions.append(" to cancel", style=GRAY_TEXT)
        
        # Combine
        content = Text("\n").join([search_text, instructions])
        
        return Panel(
            Align.center(content),
            title="Search",
            border_style=SPOTIFY_GREEN
        )
    
    def create_help_bar(self):
        """Creates the help/controls bar at the bottom."""
        if self.mode == 'podcast':
            controls = [
                ("Tab", "Radio Mode"),
                ("↑/↓", "Navigate"),
                ("Enter", "Select/Play"),
                ("←/→", "Switch List"),
                ("/", "Search"),
                ("Space", "Pause"),
                ("q", "Quit")
            ]
        else:
            controls = [
                ("Tab", "Podcast Mode"),
                ("↑/↓", "Navigate"),
                ("Enter", "Play"),
                ("Space", "Pause"),
                ("/", "Search"),
                ("q", "Quit")
            ]
        
        text_parts = []
        for key, desc in controls:
            text_parts.append(Text(f"{key}", style=f"bold {SPOTIFY_GREEN}"))
            text_parts.append(Text(f" {desc}  ", style=GRAY_TEXT))
        
        return Panel(
            Align.center(Text("").join(text_parts)),
            border_style=SPOTIFY_GREEN
        )
    
    def create_layout(self):
        """Creates the main layout."""
        layout = Layout()
        
        # Adjust layout based on search mode
        if self.search_mode:
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="main"),
                Layout(name="search", size=5),
                Layout(name="footer", size=3)
            )
        else:
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="main"),
                Layout(name="footer", size=3)
            )
        
        # Different layouts for different modes
        if self.mode == 'podcast':
            layout["main"].split_row(
                Layout(name="podcasts", ratio=1),
                Layout(name="episodes", ratio=1),
                Layout(name="player", ratio=2)
            )
        else:
            layout["main"].split_row(
                Layout(name="channels", ratio=1),
                Layout(name="player", ratio=2)
            )
        
        # Header with clock and mode indicator
        current_time = time.strftime("%H:%M:%S")
        title = Text("SR TUI", style=f"bold {SPOTIFY_GREEN}")
        mode_indicator = f" [{self.mode.upper()}]"
        subtitle = Text(f" - Sveriges Radio{mode_indicator}", style=GRAY_TEXT)
        clock = Text(f" {current_time}", style=GRAY_TEXT)
        header_text = Text("").join([title, subtitle, clock])
        layout["header"].update(Panel(Align.center(header_text)))
        
        # Main content
        if self.mode == 'podcast':
            layout["podcasts"].update(self.create_podcast_list())
            layout["episodes"].update(self.create_episode_list())
        else:
            layout["channels"].update(self.create_channel_list())
        layout["player"].update(self.create_now_playing())
        
        # Search panel (if active)
        if self.search_mode:
            layout["search"].update(self.create_search_panel())
        
        # Footer
        layout["footer"].update(self.create_help_bar())
        
        return layout
    
    def handle_input(self):
        """Handles keyboard input in a non-blocking way."""
        
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            # Check if stdin is a TTY before setting cbreak mode
            if not sys.stdin.isatty():
                logging.error("stdin is not a TTY, cannot handle input")
                return
            
            tty.setcbreak(sys.stdin.fileno())
            logging.info("Input handler started successfully")
            
            while self.running:
                try:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        char = sys.stdin.read(1)
                        
                        if char == 'q':
                            self.running = False
                        
                        elif char == ' ':  # Spacebar
                            self.toggle_pause()
                        
                        elif char == '\t':  # Tab
                            self.toggle_mode()
                        
                        elif char == '/':  # Search
                            self.enter_search_mode()
                        
                        elif char == '\n' or char == '\r':  # Enter
                            if self.mode == 'radio':
                                filtered = self.get_filtered_channels()
                                if filtered and self.selected_index < len(filtered):
                                    self.play_channel(filtered[self.selected_index])
                            elif self.mode == 'podcast':
                                if self.active_podcast_pane == 'programs':
                                    filtered_podcasts = self.get_filtered_podcasts()
                                    if filtered_podcasts and self.selected_podcast_index < len(filtered_podcasts):
                                        # Fetch episodes for selected podcast
                                        podcast = filtered_podcasts[self.selected_podcast_index]
                                        self.episodes = [] # Clear old
                                        self.get_episodes(podcast['id'])
                                        self.active_podcast_pane = 'episodes'
                                        self.selected_episode_index = 0
                                elif self.active_podcast_pane == 'episodes':
                                    filtered_episodes = self.get_filtered_episodes()
                                    if filtered_episodes and self.selected_episode_index < len(filtered_episodes):
                                        self.play_episode(filtered_episodes[self.selected_episode_index])

                        elif char == '\x1b':  # Escape sequence
                            next1 = sys.stdin.read(1)
                            if next1 == '[':
                                next2 = sys.stdin.read(1)
                                if next2 == 'A':  # Up
                                    if self.mode == 'radio':
                                        self.selected_index = max(0, self.selected_index - 1)
                                    else:
                                        if self.active_podcast_pane == 'programs':
                                            self.selected_podcast_index = max(0, self.selected_podcast_index - 1)
                                        else:
                                            self.selected_episode_index = max(0, self.selected_episode_index - 1)
                                elif next2 == 'B':  # Down
                                    if self.mode == 'radio':
                                        filtered = self.get_filtered_channels()
                                        self.selected_index = min(len(filtered) - 1, self.selected_index + 1)
                                    else:
                                        if self.active_podcast_pane == 'programs':
                                            filtered_podcasts = self.get_filtered_podcasts()
                                            self.selected_podcast_index = min(len(filtered_podcasts) - 1, self.selected_podcast_index + 1)
                                        else:
                                            filtered_episodes = self.get_filtered_episodes()
                                            self.selected_episode_index = min(len(filtered_episodes) - 1, self.selected_episode_index + 1)
                                elif next2 == 'C': # Right Arrow
                                    if self.mode == 'podcast':
                                        if self.active_podcast_pane == 'programs' and self.episodes:
                                            self.active_podcast_pane = 'episodes'
                                        elif self.is_podcast_playing:
                                            self.seek(15)
                                elif next2 == 'D': # Left Arrow
                                    if self.mode == 'podcast':
                                        if self.active_podcast_pane == 'episodes':
                                            self.active_podcast_pane = 'programs'
                                        elif self.is_podcast_playing:
                                            self.seek(-15)
                            else:
                                # Just escape - clear filter
                                self.filter_text = ""
                                self.selected_index = 0
                except Exception as e:
                    logging.error(f"Input loop error: {e}", exc_info=True)
                    # Don't crash the loop, try to continue
                    time.sleep(0.1)
        except Exception as e:
            logging.critical(f"Fatal input handler error: {e}", exc_info=True)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            logging.info("Input handler stopped")
    
    def enter_search_mode(self):
        """Enters search mode to filter channels/podcasts."""
        self.search_mode = True
        self.search_buffer = self.filter_text  # Start with current filter
        
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            
            while self.search_mode:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    
                    if char == '\n' or char == '\r':  # Enter - apply search
                        self.filter_text = self.search_buffer
                        self.selected_index = 0
                        self.selected_podcast_index = 0
                        self.selected_episode_index = 0
                        self.search_mode = False
                        break
                    elif char == '\x1b':  # Escape - cancel search
                        self.search_buffer = ""
                        self.search_mode = False
                        break
                    elif char == '\x7f':  # Backspace
                        self.search_buffer = self.search_buffer[:-1]
                    elif char.isprintable():
                        self.search_buffer += char
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    def run(self):
        """Main run loop."""
        # Fetch channels
        if not self.get_channels():
            console.print("[red]Failed to fetch channels. Exiting.[/red]")
            return
        
        if not self.channels:
            console.print("[red]No channels available. Exiting.[/red]")
            return
        
        # Start metadata update thread
        metadata_thread = threading.Thread(target=self.update_metadata, daemon=True)
        metadata_thread.start()
        
        # Start podcast position thread
        pos_thread = threading.Thread(target=self.update_podcast_position, daemon=True)
        pos_thread.start()
        
        # Start input handler thread
        input_thread = threading.Thread(target=self.handle_input, daemon=True)
        input_thread.start()
        
        # Main display loop
        try:
            with Live(self.create_layout(), refresh_per_second=4, screen=True) as live:
                while self.running:
                    live.update(self.create_layout())
                    time.sleep(0.25)
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            if self.mpv_process and self.mpv_process.poll() is None:
                self.mpv_process.terminate()
            console.print("\n[green]Thanks for listening! 👋[/green]")

def main():
    parser = argparse.ArgumentParser(description="SR CLI - Listen to Sveriges Radio")
    parser.add_argument("channel", nargs="?", help="Name of the channel to play (e.g., p3)")
    args = parser.parse_args()
    
    player = SRPlayer()
    
    if args.channel:
        # Fetch channels first
        if not player.get_channels():
            console.print("[red]Could not fetch channels.[/red]")
            sys.exit(1)
        
        # Find and play the requested channel
        search = args.channel.lower()
        selected_channel = None
        
        for c in player.channels:
            if c['name'].lower() == search:
                selected_channel = c
                break
        
        if not selected_channel:
            for c in player.channels:
                if search in c['name'].lower():
                    selected_channel = c
                    break
        
        if selected_channel:
            player.play_channel(selected_channel)
            # Set as selected in UI
            for i, ch in enumerate(player.channels):
                if ch['id'] == selected_channel['id']:
                    player.selected_index = i
                    break
    
    player.run()

if __name__ == "__main__":
    main()