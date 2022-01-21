# cPanel-DNS-UAPI
cPanel DNS UAPI for TXT records (ACME validation)

# Arguments
ADD FQDN TOKEN\
DELETE FQDN TOKEN

EXAMPLE: ADD _acme-challenge.example.com DGyRejmCefe7v4NfDGDKfA')

# How to use

This script leverages the functionality of cPanel UAPI (https://api.docs.cpanel.net/cpanel/introduction/) to allow users or other applications to create TXT records on a specified DNS Zone.

You can use it manually: [./cpanel-dns.api.py ADD _acme-challenge.example.com $TOKEN] or with an automation script like WIN-ACME: (https://www.win-acme.com)

DnsCreateScript: C:\cpanel-dns-api.exe\
DnsCreateScriptArguments: ADD {RecordName} {Token}\
DnsDeleteScriptArguments: DELETE {RecordName} {Token}

(https://www.win-acme.com/reference/plugins/validation/dns/script)
