#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py 
Author: "Aliza Jafferi Syeda"
Semester: "Fall 2024"

Description: This script monitors memory usage of processes running on a Linux system. It retrieves and displays the memory usage statistics, including total memory, available memory, and process-specific memory usage. The script allows users to visualize memory consumption in a graphical format, either in kilobytes or human-readable units.
'''

import os
import argparse

def parse_command_args():
    parser = argparse.ArgumentParser(description="Memory Visualizer -- See Memory Usage Report with bar charts \n\n Copyright 2023")
    parser.add_argument('-H', '--human-readable', action='store_true', help='Display sizes in human-readable format.')
    parser.add_argument('-l', '--length', type=int, default=20, help='Specify the graph length (default is 20).')
    parser.add_argument('program', nargs='?', type=str, help='Program name to display memory usage for its processes.')
    return parser.parse_args()

def pids_of_prog(program):
    try:
        return os.popen(f'pidof {program}').read().strip().split()
    except Exception:
        return []

def rss_mem_of_pid(pid):
    """Calculates RSS memory usage of a given PID from /proc/[pid]/smaps."""
    rss = 0
    try:
        with open(f'/proc/{pid}/smaps', 'r') as smaps_file:
            for line in smaps_file:
                if line.startswith('Rss:'):
                    rss += int(line.split()[1])  # Add the RSS value (in KB)
    except FileNotFoundError:
        print(f"ERROR: PID {pid} does not exist or /proc/{pid}/smaps is inaccessible.")
    except Exception as e:
        print(f"Unexpected error while reading /proc/{pid}/smaps: {e}")
    return rss

def human_readable_format(size_kb):
    units = ['KiB', 'MiB', 'GiB', 'TiB']
    size = float(size_kb)
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TiB"

def percent_to_graph(percent, length):
    filled = int(round(percent * length))
    return '#' * filled + ' ' * (length - filled)

def get_sys_mem():
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    return int(line.split()[1])
    except Exception:
        return 0

def get_avail_mem():
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemAvailable:'):
                    return int(line.split()[1])
    except Exception:
        return 0

def display_process_memory(program, pids, human_readable, graph_length):
    total_mem = get_sys_mem()
    total_rss = 0
    for pid in pids:
        rss = rss_mem_of_pid(pid)
        total_rss += rss
        graph = percent_to_graph(rss / total_mem, graph_length)
        percent = (rss / total_mem) * 100
        if human_readable:
            print(f"{pid:<10} [{graph}| {percent:>3.0f}%] {human_readable_format(rss)}/{human_readable_format(total_mem)}")
        else:
            print(f"{pid:<10} [{graph}| {percent:>3.0f}%] {rss}/{total_mem}")
    graph = percent_to_graph(total_rss / total_mem, graph_length)
    percent = (total_rss / total_mem) * 100
    if human_readable:
        print(f"{program:<10} [{graph}| {percent:>3.0f}%] {human_readable_format(total_rss)}/{human_readable_format(total_mem)}")
    else:
        print(f"{program:<10} [{graph}| {percent:>3.0f}%] {total_rss}/{total_mem}")

def display_system_memory(human_readable, graph_length):
    total_mem = get_sys_mem()
    avail_mem = get_avail_mem()
    used_mem = total_mem - avail_mem
    graph = percent_to_graph(used_mem / total_mem, graph_length)
    if human_readable:
        print(f"Memory         [{graph}| {100 * (used_mem / total_mem):>3.0f}%] {human_readable_format(used_mem)}/{human_readable_format(total_mem)}")
    else:
        print(f"Memory         [{graph}| {100 * (used_mem / total_mem):>3.0f}%] {used_mem}/{total_mem}")

def main():
    args = parse_command_args()
    if args.program:
        pids = pids_of_prog(args.program)
        if not pids:
            print(f"{args.program} not found.")
        else:
            display_process_memory(args.program, pids, args.human_readable, args.length)
    else:
        display_system_memory(args.human_readable, args.length)

if __name__ == '__main__':
    main()
