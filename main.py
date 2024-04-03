import time
import os
import shutil
from tasks import get_system_info_table, get_cpu_memory_table, processes_table, get_disk_info, get_gpu_info, get_open_ports, test_speed, get_net_speed
from drawyourdirs import draw_tree
from art import ascii_art
import itertools
import sys
import threading

# ANSI escape codes for colors
class TermColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    """Clears the terminal screen."""
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For Linux and Mac
    else:
        os.system('clear')

def print_in_squares(data, width):
    """Prints the given data in squares."""
    # Calculate the number of characters per line
    term_width = shutil.get_terminal_size().columns
    chars_per_section = term_width // width

    # Ensure each section is the same length
    sections = [section.split('\n') for section in data]
    max_lines = max(len(section) for section in sections)
    for section in sections:
        section.extend([''] * (max_lines - len(section)))

    # Print the sections side by side
    for line_parts in zip(*sections):
        print("".join(part.ljust(chars_per_section) for part in line_parts))

def get_section_output():
    """Gets the output for each section."""
    return [
        TermColors.HEADER + "Tree" + TermColors.ENDC + "\n" + draw_tree(2, 5),
        TermColors.HEADER + "System Information" + TermColors.ENDC + "\n" + get_system_info_table(),
        TermColors.OKBLUE + "CPU Usage (updated every few ms)" + TermColors.ENDC + "\n" + processes_table(),
        TermColors.WARNING + "Disk Information" + TermColors.ENDC + "\n" + get_disk_info(),
        TermColors.FAIL + "GPU Information" + TermColors.ENDC + "\n" + get_gpu_info(),
        TermColors.OKCYAN + "Open Ports" + TermColors.ENDC + "\n" + get_open_ports(),
        TermColors.BOLD + "CPU & Memory Table" + TermColors.ENDC + "\n" + get_cpu_memory_table(),
        TermColors.UNDERLINE + "Network Speed" + TermColors.ENDC + "\n" + test_speed(),
        TermColors.UNDERLINE + "Network Health" + TermColors.ENDC + "\n" + get_net_speed(),
    ]

loading_finished = False

def loading_screen():
    """Displays a loading animation until the loading_finished flag is set to True."""
    symbols = itertools.cycle(['-', '\\', '|', '/'])
    while not loading_finished:
        sys.stdout.write(TermColors.OKGREEN + TermColors.BOLD + '\rLoading ' + next(symbols) + TermColors.ENDC)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * 20 + '\r')  # Clear the loading message
    sys.stdout.flush()

def fetch_section_output(queue):
    """Fetches the section output and puts it into the queue, then sets the loading_finished flag."""
    global loading_finished
    sections = get_section_output()
    queue.put(sections)
    loading_finished = True  # Signal that loading is finished

    


def print_system_monitor():
    """Prints system monitor information to the CLI, updating every few seconds."""

    # Create an Event object to signal when the sections are ready
    sections_ready = threading.Event()

    # This inner function will run in a separate thread to fetch the section output
    def fetch_sections():
        sections = get_section_output()
        sections_ready.set()  # Signal that the sections are ready
        return sections

    # Start the thread to fetch sections
    fetch_thread = threading.Thread(target=fetch_sections)
    fetch_thread.start()

    # While the sections are being fetched, show the loading screen
    while not sections_ready.is_set():
        loading_screen()

    # Once the sections are ready, we can retrieve them
    fetch_thread.join()  # Wait for the thread to finish if it hasn't already
    sections = fetch_thread.result  # Get the result from the thread

    # Now that we have the sections, we can print them and update them regularly
    while True:
        clear_screen()
        ascii_art()
        print_in_squares(sections, 2)  # Adjust the width as necessary for your layout
        time.sleep(3)  # Sleep for a few seconds before updating again
        sections = get_section_output()  # Get updated section output

# Run the system monitor in the CLI
print_system_monitor()