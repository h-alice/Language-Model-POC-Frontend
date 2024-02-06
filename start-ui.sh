#!/bin/bash

# Define colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
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
#

# Display a warning banner if user's Python version doesn't match requirements.
python_version_check() {

    current_python_version=$(python3 --version 2>&1 | awk '{print $2}')
    required_python_version="3.11.0"
    if [[ "$(printf "%s\n" "$required_python_version" "$current_python_version" | sort -V | head -n1)" == "$current_python_version" ]]; then
        printf "${YELLOW}Current Python version (${current_python_version}) is smaller then required version (${required_python_version}).${NC}\n"
        printf "${YELLOW}This project may not work as expected.${NC}\n\n"
    else
        printf "${CYAN}Current Python version: ${YELLOW}${current_python_version} ${NC}\n"
    fi
    return 0
}

create_venv() {

    printf "${YELLOW}Creating Python virtual environment in .venv folder...${NC}\n"

    if python3 -m venv .venv; then
        printf "${GREEN}Successfully created environment.${NC}\n"
        echo "*" > .venv/.gitignore
        return 0
    else
        printf "${RED}Cannot create environment.${NC}\n"
        return 1
    fi
}

check_package_installation() {
    local package_name="$1"
    local desired_version="$2"

    if python -m pip show "$package_name" &>/dev/null; then
        
        if [ -n "$desired_version" ]; then
            installed_version=$(python -m pip show "$package_name" | grep Version | awk '{print $2}')
            
            if [ "$installed_version" == "$desired_version" ]; then
                printf "${package_name} ${desired_version} is installed.\n"
                return 0
            else
                printf "${YELLOW}Version mismatch for ${package_name}: Installed ${installed_version}, Required version: ${desired_version}\n${NC}"
                return 1
            fi
        else
            printf "${package_name} is installed.\n"
            return 0
        fi
    else
        printf "${YELLOW}${package_name} is not installed.\n"
        return 1
    fi
}

# Check if environment exists
if [ -d ".venv" ]; then
    printf "${CYAN}Existing virtual environment (.venv) found.${NC}\n"
    
    # Try activating the existing virtual environment
    printf "${CYAN}Activating virtual environment...${NC}\n"
    if source .venv/bin/activate; then
        printf "\n"
        python_version_check
    else
        printf "${RED}Failed to activate existing virtual environment. Re-creating environment.${NC}\n\n"
        rm -rf .venv

        if create_venv; then
            source .venv/bin/activate
            printf "\n"
            python_version_check
        else
            exit 1
        fi
    fi
fi

# Install requirement.
printf "\n${CYAN}Checking package installation...${NC}\n"
pip install --disable-pip-version-check -q -r requirements.txt

printf "\n${GREEN}Environment integrity checked, starting webui.${NC}\n"

streamlit run webui.py --browser.gatherUsageStats False --server.address "0.0.0.0"






