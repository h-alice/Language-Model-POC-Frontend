#!/bin/bash

## Constants

# Certificate information
COMMON_NAME="lmpoc.taipei"
ORGANIZATION_NAME="Taipei City Government"
ORGANIZATIONAL_UNIT="Department of Information Technology"
LOCALITY="Taipei"
STATE="Taiwan"
COUNTRY_CODE="TW"

# Output folder for certificate and private key
OUTPUT_FOLDER=".cert"

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
        printf "${YELLOW}[!] Current Python version (${current_python_version}) is smaller then required version (${required_python_version}).${NC}\n"
        printf "${YELLOW}[!] This project may not work as expected.${NC}\n\n"
    else
        printf "${CYAN}[+] Current Python version: ${YELLOW}${current_python_version} ${NC}\n"
    fi
    return 0
}

create_venv() {

    printf "${YELLOW}[*] Creating Python virtual environment in .venv folder...${NC}\n"

    if python3 -m venv .venv; then
        printf "${GREEN}[+] Successfully created environment.${NC}\n"
        echo "*" > .venv/.gitignore
        return 0
    else
        printf "${RED}[x] Cannot create environment.${NC}\n"
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
                printf "[+] ${package_name} ${desired_version} is installed.\n"
                return 0
            else
                printf "${YELLOW}[!] Version mismatch for ${package_name}: Installed ${installed_version}, Required version: ${desired_version}\n${NC}"
                return 1
            fi
        else
            printf "[*] ${package_name} is installed.\n"
            return 0
        fi
    else
        printf "${YELLOW}[!] ${package_name} is not installed.\n"
        return 1
    fi
}

activate_or_recreate_venv() {
    # Try activating the existing virtual environment
    printf "${CYAN}[*] Activating virtual environment...${NC}\n"
    if source .venv/bin/activate; then
        printf "\n"
        python_version_check
    else
        printf "${RED}[x] Failed to activate existing virtual environment. Re-creating environment.${NC}\n\n"
        rm -rf .venv

        if create_venv; then
            source .venv/bin/activate
            printf "\n"
            python_version_check
        else
            exit 1
        fi
    fi
}

# Check if environment exists
if [ -d ".venv" ]; then
    printf "${CYAN}[*] Existing virtual environment (.venv) found.${NC}\n"
    activate_or_recreate_venv
else
    create_venv
    activate_or_recreate_venv
fi

# Install requirement.
printf "\n${CYAN}[*] Checking package installation...${NC}\n"
pip install --disable-pip-version-check -q -r requirements.txt

printf "\n${GREEN}[+] Environment integrity checked, starting webui.${NC}\n"

## Certification

# Check if certificate and private key already exist
if [ -f "$OUTPUT_FOLDER/webapp-selfsigned.crt" ] && [ -f "$OUTPUT_FOLDER/webapp-selfsigned.key" ]; then
    printf "${CYAN}[*] Certificate and private key already exist. Skipping self-signed certificate creation.${NC}\n\n"
    
else
    printf "${CYAN}[*] Creating self-signed certificate.${NC}\n\n"
    # Create output folder if it doesn't exist
    mkdir -p "$OUTPUT_FOLDER"
    echo "*" > "$OUTPUT_FOLDER"/.gitignore

    # Generate private key using ECDSA
    openssl ecparam -name prime256v1 -genkey -noout -out "$OUTPUT_FOLDER/webapp-selfsigned.key"

    # Generate certificate signing request (CSR)
    openssl req -new -key "$OUTPUT_FOLDER/webapp-selfsigned.key" -out "$OUTPUT_FOLDER/webapp-selfsigned.csr" -subj "/C=${COUNTRY_CODE}/ST=${STATE}/L=${LOCALITY}/O=${ORGANIZATION_NAME}/OU=${ORGANIZATIONAL_UNIT}/CN=${COMMON_NAME}"

    # Generate self-signed certificate
    openssl x509 -req -days 365 -in "$OUTPUT_FOLDER/webapp-selfsigned.csr" -signkey "$OUTPUT_FOLDER/webapp-selfsigned.key" -out "$OUTPUT_FOLDER/webapp-selfsigned.crt"

    # Output success message
    printf "${GREEN}[+] Certificate and private key generated successfully.${NC}\n\n"

fi

streamlit run webui.py --browser.gatherUsageStats False --server.address "0.0.0.0" --server.port "443" --server.sslCertFile .cert/webapp-selfsigned.crt --server.sslKeyFile .cert/webapp-selfsigned.key






