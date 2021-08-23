#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ ! -f "$HOME/bin/fleet" ]
then
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

    echo -n '{ "flounder": { "username": "' > "$DIR/secrets.json"
    read -p 'Flounder username: ' -r
    echo -n "$REPLY" >> secrets.json
    echo -n '", "password": "' >> secrets.json
    read -p 'Flounder password: ' -r -s
    echo -n "$REPLY" >> secrets.json
    echo -n '" } }' >> secrets.json
    echo -e "\033[32mDone.\033[0m"
    echo "(If you wish to change the submitted data, you can edit $DIR/secrets.json directly.)"
fi
