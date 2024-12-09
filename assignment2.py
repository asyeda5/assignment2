 #!/usr/bin/python3
 
 
import os
import argparse

def parse_command_args():
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts")
    parser.add_argument('-H', '--human-readable', action='store_true', help='Prints sizes in human readable format')
    parser.add_argument('-l', '--length', type=int, default=20, help='Specify the length of the graph. Default is 20.')
    parser.add_argument('program', nargs='?', type=str, help='If a program is specified, show memory use of all associated processes.')
    return parser.parse_args()

def pids_of_prog(program):
    pids = []
    try:
        pids = os.popen(f'pidof {program}').read().split()
        if not pids:
            print(f"No PIDs found for program: {program}")
    except Exception as e:
        print(f"Error retrieving PIDs: {e}")
    return pids

def rss_mem_of_pid(pid):
    rss_memory = 0
    try:
        # Ensure the pid is valid and the path exists
        pid_path = f'/proc/{pid}/smaps'
        if os.path.exists(pid_path):
            with open(pid_path, 'r') as f:
                for line in f:
                    if line.startswith('Rss:'):
                        rss_memory += int(line.split()[1])
        else:
            print(f"Unable to open {pid_path} for memory usage.")
    except IOError as e:
        print(f"Error opening {pid_path}: {e}")
    return rss_memory

def human_readable_format(size_in_kb):
    units = ['KiB', 'MiB', 'GiB', 'TiB']
    size = size_in_kb
    unit = units[0]
    for u in units:
        if size < 1024:
            unit = u
            break
        size /= 1024
    return f"{size:.2f} {unit}"

def percent_to_graph(pcnt, max_length):
    pcnt = max(0, min(pcnt, 1))
    num_hashes = int(pcnt * max_length)
    bar = '#' * num_hashes + ' ' * (max_length - num_hashes)
    return bar

def get_sys_mem():
    total_mem = 0
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    total_mem = int(line.split()[1])
                    break
    except IOError:
        pass
    return total_mem

def get_avail_mem():
    avail_mem = 0
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemAvailable:'):
                    avail_mem = int(line.split()[1])
                    break
    except IOError:
        pass
    return avail_mem

def main():
    args = parse_command_args()

    if args.program:
        pids = pids_of_prog(args.program)
        if not pids:
            print(f"No processes found for program: {args.program}")
            return

        print(f"Memory usage for processes of {args.program}:")
        for pid in pids:
            rss = rss_mem_of_pid(pid)
            print(f"PID {pid}: {rss} KB")
            if args.human_readable:
                print(f"Human-readable: {human_readable_format(rss)}")
    else:
        print("No program specified, showing total system memory usage.")
        total_memory = get_sys_mem()
        available_memory = get_avail_mem()
        print(f"Total Memory: {total_memory} KB")
        print(f"Available Memory: {available_memory} KB")
        if args.human_readable:
            print(f"Total Memory (Human-readable): {human_readable_format(total_memory)}")
            print(f"Available Memory (Human-readable): {human_readable_format(available_memory)}")
        
    max_length = args.length
    bar = percent_to_graph(available_memory / total_memory, max_length)  # Graph for available memory
    print(f"Memory Usage Bar Graph: {bar}")

if __name__ == '__main__':
    main()
