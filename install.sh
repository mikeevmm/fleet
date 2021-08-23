#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo -e "Checking whether python3 is present..."
if command -v python3 >/dev/null 2>&1
then
        echo -e "\033[32mFound.\033[0m"
else
        echo -e "\033[91mCould not find Python3.\033[0m"
fi

echo ''
echo -e "This script will install the requirements listed in "
echo -e "$DIR/requirements.txt"
echo -e "using python3 -m pip install -r .../requirements.txt"
echo -e "You can do this yourself manually later."
echo ''
read -p $'\033[33mInstall dependencies? [Y/n]?\033[0m ' -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    python3 -m pip install -r "$DIR/requirements.txt"
    if [ ! $? -eq 0 ]
    then
        echo -e "\033[91mSomething went wrong.\033[0m"
        exit 1
    fi
fi

if [ ! -f "$HOME/bin/fleet" ]
then
    echo ''
    echo -e "This script will add a symlink from"
    echo -e "$HOME/bin/fleet"
    echo -e "to"
    echo -e "$DIR/fleet.py"
    echo -e "so that you can call fleet from any directory."
    read -p $'\033[33mIs this ok [N/y]?\033[0m ' -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
    fi

    if [ ! -d $HOME/bin ]; then
        echo ''
        echo -e "$HOME/bin does not exist, creating that directory."
        read -p '\033[33mIs this ok [N/y]?\033[0m ' -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]
        then
            [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
        fi
        mkdir $HOME/bin
        export PATH="$HOME/bin:$PATH"
        echo -e "\033[32mCreated $HOME/bin\033[0m"
    fi

    if ln -s "$DIR/fleet.py" "$HOME/bin/fleet"
    then
        echo -e "\033[32mDone.\033[0m"
    else
        echo -e "\033[91mSomething went wrong.\033[0m"
    fi
fi

if [ ! -f "$DIR/secrets.json" ]
then
    echo ''
    echo 'Some further setup is needed to allow fleet to connect to Flounder'
    echo 'and upload your posts.'
    echo '(Consider going through the source of install.sh at this point '
    echo 'to make sure that I'"'"'m not stealing your credentials.)'
    echo ''

    echo -n '{ "flounder": { "user": "' > "$DIR/secrets.json"
    read -p 'Flounder username: ' -r
    echo -n "$REPLY" >> secrets.json
    echo -n '", "password": "' >> secrets.json
    read -p 'Flounder password: ' -r -s
    echo -n "$REPLY" >> secrets.json
    echo -n '" } }' >> secrets.json
    echo -e "\033[32mDone.\033[0m"
    echo "(If you wish to change the submitted data, you can edit $DIR/secrets.json directly.)"
fi
