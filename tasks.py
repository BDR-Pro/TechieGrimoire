import psutil
import GPUtil
import socket
import subprocess
import os
from datetime import datetime
import platform
from tabulate import tabulate 
from functools import cache


def ports_name(port):
    """Get the name of the port."""
    try:
        return socket.getservbyport(port, 'tcp')
    except OSError:
        return None
@cache
def get_open_ports():
    """Get open ports on the system."""
    open_ports = []
    for port in range(1, 1024):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.1)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                service_name = ports_name(port)
                if service_name:
                    open_ports.append(f"{port} ({service_name})")
                else:
                    open_ports.append(str(port))
    ports_str = ', '.join(open_ports)
    return ports_str

@cache
def test_speed():
    '''Function to get speed of the internet connection using speedtest-cli'''
    speed = subprocess.run(['speedtest-cli', '--simple'], capture_output=True, text=True)
    return speed.stdout

# Function to retrieve and format network speed
def get_net_speed():
    counters = psutil.net_io_counters()
    connection_info = ""
    connection_info += f"Sent: {calc_size(counters.bytes_sent)}\n"
    connection_info += f"Received: {calc_size(counters.bytes_recv)}\n"
    
    # Check if we have any connection information for Wi-Fi
    #psutil.net_connections() gives us the socket connections
    net_connections = psutil.net_connections(kind='inet')
    connections = [f"{c.laddr.ip}:{c.laddr.port} -> {c.raddr.ip}:{c.raddr.port}"
                    for c in net_connections if c.laddr and c.raddr]
    
    # Only display a certain number of connections, not to overload the GUI
    max_display = 25
    connection_info += f"Connections: {(len(connections))} (showing up to {max_display})\n"
    connection_info += "\n".join(connections[:max_display])
    connection_info += "\n"
    # Continue with net speed information

    return connection_info


def calc_size(size):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return '{:.2f} {}'.format(size, unit)

def get_cpu_memory_table():
    # Fetching overall CPU usage
    overall_cpu_usage = psutil.cpu_percent()
    
    # Fetching per-core CPU usage
    per_core_usage = psutil.cpu_percent(percpu=True, interval=1)
    
    # Fetching memory usage
    memory = psutil.virtual_memory()
    memory_percentage = memory.percent
    memory_used = calc_size(memory.used)
    memory_total = calc_size(memory.total)
    
    # Preparing data for tabulation
    data = [
        ["Overall CPU Usage", f"{overall_cpu_usage}%"],
        ["Total Memory", memory_total],
        ["Memory Used", memory_used],
        ["Memory Usage", f"{memory_percentage}%"]
    ]
    
    # Adding per-core CPU usage
    for i, percentage in enumerate(per_core_usage):
        data.append([f"CPU Core {i+1}", f"{percentage}%"])
    
    # Creating table
    table = tabulate(data, headers=["Metric", "Value"], tablefmt="grid")
    return table

# Function to get disk information
def get_disk_info():

    partitions = psutil.disk_partitions()
    for p in partitions:
        usage = psutil.disk_usage(p.mountpoint)
        disk_info = f"{p.device}: {usage.percent}% used\n"
        disk_info += f" ({usage.used / 1024 / 1024 / 1024:.2f} GB)\n"
        disk_info += f" out of {usage.total / 1024 / 1024 / 1024:.2f} GB\n"
        disk_info += f" on {p.mountpoint}\n"
        disk_info += f" ({p.fstype})\n"
    return disk_info
# Function to retrieve and format current process information

def get_process_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        processes.append(proc.info)
    # Sort the processes by CPU usage descending
    processes = sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)
    return processes


def processes_table():
    process_list = get_process_info()
    # Define headers for our table
    headers = ['PID', 'Name', 'Username', 'CPU %', 'Memory %']
    # Extract the information in a list of lists for tabulate
    table_data = [[proc['pid'], proc['name'], proc['username'], proc['cpu_percent'], proc['memory_percent']] for proc in process_list]
    # Print the table
    return (tabulate(table_data, headers=headers, tablefmt="grid"))
    
# Function to retrieve and format GPU information
def get_gpu_info():
    gpus = GPUtil.getGPUs()
    gpu_info = ""
    for gpu in gpus:
        gpu_info += f"GPU: {gpu.name}\n"
        gpu_info += f"Load: {gpu.load*100:.1f}%\n"
        gpu_info += f"Temperature: {gpu.temperature} C\n"
        gpu_info += f"Memory Used: {gpu.memoryUsed:.1f}/{gpu.memoryTotal:.1f} MB\n"
        gpu_info += f"UUID: {gpu.uuid}\n"
        gpu_info += f"Driver: {gpu.driver}\n"
        gpu_info += f"Serial: {gpu.serial}\n"
        gpu_info += f"Display Mode: {gpu.display_mode}\n"
        gpu_info += f"Display Active: {gpu.display_active}\n"
        gpu_info += f"Max Memory Used: {gpu.memoryTotal:.1f} MB\n"
    return gpu_info

def my_public_ip(ip_version=4):
    '''Function to get public IP address using IPv4 or IPv6.'''
    ip_version_option = '-4' if ip_version == 4 else '-6'
    try:
        ip = subprocess.run(['curl', ip_version_option, 'ifconfig.me'], capture_output=True, text=True, check=True)
        return ip.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error fetching IP: {e}"

def get_local_ip():
    '''Reliably fetch the local IPv4 address.'''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP




def get_system_info_table():
    """Generate a table of system information."""
    info = [
        ["User", os.getlogin()],
        ["Host Name", platform.node()],
        ["Operating System", platform.system()],
        ["OS Version", platform.version()],
        ["OS Release", platform.release()],
        ["Machine", platform.machine()],
        ["Processor", platform.processor()],
        ["Architecture", platform.architecture()[0]],
        ["Python Version", platform.python_version()],
        ["Boot Time", datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")],
        ["Physical Cores", psutil.cpu_count(logical=False)],
        ["Logical Cores", psutil.cpu_count(logical=True)],
        ["Number of Processes", len(psutil.pids())],
        ["Number of Users", len(psutil.users())],
        ["Max Frequency", f"{psutil.cpu_freq().max:.2f}Mhz"],
        ["Min Frequency", f"{psutil.cpu_freq().min:.2f}Mhz"],
        ["Current Frequency", f"{psutil.cpu_freq().current:.2f}Mhz"],
        ["System Load Average", os.getloadavg() if hasattr(os, 'getloadavg') else "Not available on this platform"],
        ["Uptime", datetime.now() - datetime.fromtimestamp(psutil.boot_time())],
        ["Public IPv4", my_public_ip(4)],
        ["Public IPv6", my_public_ip(6)],
        ["Local IPv4", get_local_ip()]
    ]
    # The 'grid' format is just one of many styles tabulate supports
    return tabulate(info, headers=["System", "Features"], tablefmt="grid")


