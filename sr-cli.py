#!/usr/bin/env python3
import requests
import sys
import argparse
import subprocess
import time
import shutil
import os
import threading

# Base URL for SR API
BASE_URL = "https://api.sr.se/api/v2"

def get_channels():
    """
    Fetches the list of channels from the SR API using JSON format.
    """
    channels = []
    next_page_url = f"{BASE_URL}/channels?format=json&pagination=false"

    try:
        response = requests.get(next_page_url)
        response.raise_for_status()
        data = response.json()
        
        if 'channels' in data:
            channels.extend(data['channels'])

    except requests.exceptions.RequestException as e:
        print(f"Error fetching channels: {e}", file=sys.stderr)
        return []
    except ValueError:
        return []

    return channels

def get_live_url(channel_id):
    """
    Fetches the live audio URL for a channel.
    """
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

def get_now_playing(channel_id):
    """
    Fetches current program and song metadata.
    """
    program_title = "Unknown Program"
    song_title = ""
    
    # Get scheduled episode
    try:
        prog_url = f"{BASE_URL}/scheduledepisodes/rightnow?channelid={channel_id}&format=json"
        response = requests.get(prog_url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            if 'scheduledepisode' in data:
                program_title = data['scheduledepisode'].get('title', 'Unknown Program')
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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_centered(text, width):
    print(text.center(width))

def tui_loop(channel_name, channel_id, stop_event):
    """
    Updates the UI with metadata while playing.
    """
    while not stop_event.is_set():
        width = shutil.get_terminal_size().columns
        program, song = get_now_playing(channel_id)
        
        clear_screen()
        print("\n" * 2)
        print_centered("=" * 40, width)
        print_centered(f"SR CLI - PLAYING {channel_name.upper()}", width)
        print_centered(f"{time.strftime('%H:%M:%S')}", width)
        print_centered("=" * 40, width)
        print("\n")
        
        print_centered(f"PROGRAM: {program}", width)
        if song:
            print_centered(f"MUSIC:   {song}", width)
            
        print("\n" * 2)
        print_centered("[ Press Ctrl+C to Stop ]", width)
        
        time.sleep(10)

def play_channel(channel_name, channel_id):
    """
    Starts playback and the TUI.
    """
    url = get_live_url(channel_id)
    if not url:
        print(f"Could not find live stream for {channel_name}")
        return

    print(f"Starting {channel_name}...")
    
    # Start mpv
    try:
        mpv_process = subprocess.Popen(
            ["mpv", "--no-video", "--quiet", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        print("Error: 'mpv' is not installed. Please install it to play audio.")
        return

    # Start TUI thread
    stop_event = threading.Event()
    tui_thread = threading.Thread(target=tui_loop, args=(channel_name, channel_id, stop_event))
    tui_thread.start()

    try:
        mpv_process.wait() # Wait for mpv to exit (or user to kill it)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        if mpv_process.poll() is None:
            mpv_process.terminate()
        tui_thread.join()
        print("\nStopped.")

def interactive_menu(channels):
    """
    Shows a list of channels and lets the user choose.
    """
    while True:
        print("\nSR CLI - Channels")
        print("-" * 20)
        for i, channel in enumerate(channels):
            print(f"[{i+1:2}] {channel['name']}")
        
        choice = input("\nSelect channel (number) or 'q' to quit: ").strip().lower()
        
        if choice == 'q':
            sys.exit(0)
            
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(channels):
                return channels[idx]
            else:
                print("Invalid number.")
        except ValueError:
            print("Invalid input.")

def main():
    parser = argparse.ArgumentParser(description="SR CLI - Listen to Sveriges Radio")
    parser.add_argument("channel", nargs="?", help="Name of the channel to play (e.g., p3)")
    args = parser.parse_args()

    channels = get_channels()
    if not channels:
        print("Could not fetch channels.")
        sys.exit(1)

    selected_channel = None

    if args.channel:
        # Direct mode
        search = args.channel.lower()
        # Try exact match first
        for c in channels:
            if c['name'].lower() == search:
                selected_channel = c
                break
        # Try partial match
        if not selected_channel:
             for c in channels:
                if search in c['name'].lower():
                    selected_channel = c
                    break
        
        if not selected_channel:
            print(f"Channel '{args.channel}' not found.")
            sys.exit(1)
    else:
        # Interactive mode
        selected_channel = interactive_menu(channels)

    if selected_channel:
        play_channel(selected_channel['name'], selected_channel['id'])

if __name__ == "__main__":
    main()