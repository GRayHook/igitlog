#!/usr/bin/python3

import subprocess
import re
import curses
import os
import sys

class Commit(object):
    _RE_COMMIT = re.compile(r"(?P<hash>[abcdefABCDEF0-9]{3,16}) (?P<title>.+)")
    def __init__(self, line):
        """@todo: to be defined1. """
        match = Commit._RE_COMMIT.search(line)
        if not match:
            raise ValueError
        self.hash = match.group("hash")
        self.title = match.group("title")

process = subprocess.Popen(["git", "log", "--oneline"], stdout=subprocess.PIPE, stderr=open('/dev/null', 'w'))
commits = []
for part in process.communicate():
    if part == None:
        break
    for line in part.decode('utf-8').split('\n'):
        if not line:
            continue
        commits.append(Commit(line))


if len(commits) == 0:
    sys.exit(0)

stdscr = curses.initscr()
curses.start_color()
curses.curs_set(False)
curses.use_default_colors()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
stdscr.refresh()
curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

maxcoords = stdscr.getmaxyx()
max_y, max_x = maxcoords[0], maxcoords[1]


def show_commit(commit):
    os.system(f"git show {commit.hash}")


pad = curses.newpad(len(commits), max_x)


def print_commit(commit, pos_y, selected):
    pad.addstr(pos_y, 0, " " * (max_x - 1))
    if selected:
        pad.addstr(pos_y, 0, f"{commit.hash}", curses.color_pair(1))
        pad.addstr(pos_y, len(commit.hash) + 2, f"{commit.title}", curses.color_pair(1))
    else:
        pad.addstr(pos_y, 0, f"{commit.hash}", curses.color_pair(2))
        pad.addstr(pos_y, len(commit.hash) + 2, f"{commit.title}")

print_commit(commits[0], 0, True)

linenum = 1
for commit in commits[1:]:
    print_commit(commit, linenum, False)
    linenum += 1

pad.refresh(0, 0, 0, 0, max_y - 1, max_x - 1)

running = True
pos = 0
offset = 0
while running:
    print_commit(commits[pos], pos, False)

    mvmt = stdscr.getch()
    if mvmt == ord('j'):
        if pos < len(commits):
            pos += 1
        if pos - offset > max_y - 2 and offset < len(commits) - max_y + 5:
            offset += 1
    elif mvmt == ord('k'):
        if pos > 0:
            pos -= 1
        if pos - offset < 4 and offset > 0:
            offset -= 1
    elif mvmt == ord('q'):
        running = False
    elif mvmt == ord('l'):
        show_commit(commits[pos])
        stdscr.clear()
        stdscr.refresh()

    print_commit(commits[pos], pos, True)

    pad.refresh(offset, 0, 0, 0, max_y - 1, max_x - 1)



curses.nocbreak()
stdscr.keypad(False)
curses.echo()
curses.endwin()
