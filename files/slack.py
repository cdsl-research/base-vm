#!/usr/bin/env python3

import requests
import json
import sys

ARGS = sys.argv[1:]
SLACK_TOKEN = ''

def slack(fqdn: str, ip_addr: str, hw_addr: str) -> None:
    # print(fqdn, ip_addr, hw_addr)
    requests.post(SLACK_TOKEN, data = json.dumps({
        'text': "FQDN is binded new client.",
        'attachments': [
            {
            "color": "good",
                "fields":[
                    {
                        "title": "FQDN",
                        "value": f'{fqdn}',
                        "short": True,
                    },
                    {
                        "title": "IP Address",
                        "value": f'{ip_addr}',
                        "short": True,
                    },
                    {
                        "title": "HW Address",
                        "value": f'{hw_addr}',
                        "short": True,
                    }
                ]
            }
        ]
    }))

if __name__ == '__main__':
    if len(ARGS) != 3:
        print("(Usage) ./notify_slack [IP_ADDRESS] [HW_ADDRESS] [Hostname]")
        sys.exit(1)

    with open('/etc/kea/slack_token') as f:
        line = f.readline()
        if line.startswith("https://hooks.slack.com/services/"):
            SLACK_TOKEN = line
        else:
            print("(Error) You should set slack token on /etc/kea/slack_token")
            sys.exit(1)
            
    slack(fqdn=ARGS[2], ip_addr=ARGS[0], hw_addr=ARGS[1])
