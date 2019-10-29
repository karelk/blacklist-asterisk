#!/usr/bin/python3

import sys, regex, socket

################################################################################################################################################################
###   sanity checks   ##########################################################################################################################################
################################################################################################################################################################

if sys.stdin.isatty():
    print('sys.stdin is not a pipe')
    sys.exit(1)

################################################################################################################################################################
###   regex   ##################################################################################################################################################
################################################################################################################################################################

IP = r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

PATTERNS = [
    '.* Registration from .* failed for \'{ip}:\d+\' - Wrong password',
    '.* Call from .* \({ip}:\d+\) to extension .* rejected because extension not found in context \'unauthenticated\'.'
]

PATTERNS_COMPILED = regex.compile('(?|%s)' % '|'.join(PATTERNS).format(ip=IP))

################################################################################################################################################################
###   functions   ##############################################################################################################################################
################################################################################################################################################################

def host_lookup(addr):
    try:
        return socket.gethostbyaddr(addr)[0]
    except socket.herror:
        return None

################################################################################################################################################################
###   main   ###################################################################################################################################################
################################################################################################################################################################

for line in sys.stdin:

    match = PATTERNS_COMPILED.search(line)
    if match:
        host_ip = match['ip']

        # this emulates "echo +1.2.3.4 > /proc/net/xt_recent/BLACKLIST"
        with open("/proc/net/xt_recent/BLACKLIST", 'w') as blacklist:
            blacklist.write(f'+{host_ip}\n')
        blacklist.close()

        with open('/var/log/firewall/asterisk.log', 'a') as f:
            f.write(line)
            f.write(f'   BLACKLIST: {host_ip} [{host_lookup(host_ip)}]\n\n')
        f.close()

