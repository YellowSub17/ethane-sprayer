#!/usr/bin/env bash

SESSION_NAME="ethane"

# 1. Start a new detached session (-d)
tmux new-session -d -s "$SESSION_NAME"

# 2. Split the window horizontally into top and bottom panes
# Note: In tmux, '-v' stacks panes vertically (creating a top/bottom split)
tmux split-window -v -t "$SESSION_NAME:1"

# 3. Split the bottom pane (pane 1) vertically into left and right panes
# Note: In tmux, '-h' places panes side-by-side (creating a left/right split)
tmux split-window -h -t "$SESSION_NAME:1.2"



tmux send-keys -t "$SESSION_NAME:1.1" "vim" C-m
tmux send-keys -t "$SESSION_NAME:1.2" "cd pico" C-m
tmux send-keys -t "$SESSION_NAME:1.3" "minicom -b 115200 -o -D /dev/ttyACM0" C-m

# 4. (Optional) Select the top pane before attaching
tmux select-pane -t "$SESSION_NAME:1.0"

# 5. Attach to the session
tmux attach-session -t "$SESSION_NAME"
