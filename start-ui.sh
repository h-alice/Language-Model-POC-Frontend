#!/bin/bash

# Define colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # Clear color.

# Display Super-Cool project title.
fancy_project_title() {
    echo -e "
\033[38;05;196m  _     __  __ ____        ____    _____ _____ \033[0m
\033[38;05;208;1m | |   |  \/  |  _ \ ___  / ___|  |  ___| ____|\033[0m
\033[38;05;220;1m | |   | |\/| | |_) / _ \| |      | |_  |  _|  \033[0m
\033[38;05;82;1m | |___| |  | |  __/ (_) | |___   |  _| | |___ \033[0m
\033[38;05;33;1m |_____|_|  |_|_|   \___/ \____|  |_|   |_____|\033[0m
${NC}
"
}

fancy_project_title

