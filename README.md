# domainctl
Bawue.Net DNS API client

 * Anzeigen aller Domains:
   ```./domainctl.py --username=benutzer --password=geheim list_domains``
 * Anzeigen aller DNS Einträge einer Domain:
   ```./domainctl.py --username=benutzer --password=geheim --domain=example.com list_domains``
 * Hinzufügen eines neuen DNS Eintrages:
   ```./domainctl.py --username=benutzer --password=geheim --domain=example.com --host=_acme-challenge --type=TXT --rr="01234abcde" add_record```
 * Entfernen eines betehenden DNS Eintrages:
   ```./domainctl.py --username=benutzer --password=geheim --domain=example.com --host=_acme-challenge --type=TXT --rr="01234abcde" add_record```
