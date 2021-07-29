#!/bin/bash

echo "Removing fleet link..."
if rm "$HOME/bin/fleet"; then
    echo -e "\033[32mDone.\033[0m"
else
    echo "Something went wrong."
fi
