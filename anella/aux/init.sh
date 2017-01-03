#!/bin/bash

tmux new-session -d -s VPN
tmux send -t VPN "cd ~/" ENTER
tmux send -t VPN "cd TeNOR/anella/keys" ENTER
tmux send -t VPN "openvpn final.ovpn" ENTER

tmux new-session -d -s TeNOR
tmux send -t TeNOR "rvm use 2.3.3" ENTER
tmux send -t TeNOR "cd ~/" ENTER
tmux send -t TeNOR "cd TeNOR/" ENTER
tmux send -t TeNOR "invoker start invoker.ini" ENTER


tmux new-session -d -s catalog
tmux send -t catalog "cd ~/" ENTER
tmux send -t catalog "cd catalog/" ENTER
tmux send -t catalog "python wsgi.py" ENTER

tmux new-session -d -s marketplace
tmux send -t marketplace "cd ~/" ENTER
tmux send -t marketplace "cd marketplace/" ENTER
tmux send -t marketplace "gulp serve" ENTER
