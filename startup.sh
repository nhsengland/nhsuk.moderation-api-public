#!/bin/sh
set -e

# Get env vars in the Dockerfile to show up in the SSH session
echo "enabling env vars through SSH..."
eval $(printenv | sed -n "s/^\([^=]\+\)=\(.*\)$/export \1=\2/p" | sed 's/"/\\\"/g' | sed '/=/s//="/' | sed 's/$/"/' >> /etc/profile)

echo "starting SSH..."
service ssh start

echo "starting flask app..."
flask run
