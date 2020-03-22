#!/bin/sh

case "$1" in
  "lease4_select")
    python3 /etc/kea/slack.py ${KEA_LEASE4_ADDRESS} ${KEA_LEASE4_HWADDR} ${KEA_LEASE4_HOSTNAME}
    ;;

esac
