# cPanel-DNS-UAPI
cPanel DNS UAPI for TXT records (ACME validation)

This script leverages the functionality of cPanel UAPI (https://api.docs.cpanel.net/cpanel/introduction/) to allow users or other applications to create TXT records on a specified DNS Zone.

## Arguments
```
ADD FQDN TOKEN
DELETE FQDN TOKEN
```

Example: ```./cpanel-dns-uapi.py ADD _acme-challenge.example.com DGyRejmCefe7v4NfDGDKfA```

## How to use
On first run, the script will create an empty **'.dns-env'** file, you will need to complete it before you can continue:
```
# cPanel-DNS-UAPI configuration file

CPANEL_DOMAIN = example.com
CPANEL_PORT = 2083
CPANEL_USERNAME = username
CPANEL_PASSWORD = password

DNS_ZONE = example.com
RECORD_TTL = 3600
```

After that, you can use it manually: [./cpanel-dns.api.py ADD _acme-challenge.example.com $TOKEN] or with an automation script like\
WIN-ACME: (https://www.win-acme.com)
```
DnsCreateScript: C:\cpanel-dns-uapi.exe
DnsCreateScriptArguments: ADD {RecordName} {Token}
DnsDeleteScriptArguments: DELETE {RecordName} {Token}
```
(https://www.win-acme.com/reference/plugins/validation/dns/script)
