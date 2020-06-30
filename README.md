#Bawue.Net DNS API client

Dieser Client erlaubt es, seine beim [https://www.bawue.net/](Bawue.Net) gehosteten Domains von der Kommandozeile aus zu administrieren.
Somit kann auf einfache Weite ein Let'sEncrypt Zertifikat mit der DNS-01 Challenge erzeugt werden.


Beispielaufruf
==============

 * Anzeigen aller Domains:
   `./domainctl.py --username=benutzer --password=geheim list_domains`
 * Anzeigen aller DNS Einträge einer Domain:
   `./domainctl.py --username=benutzer --password=geheim --domain=example.com list_domains`
 * Hinzufügen eines neuen DNS Eintrages:
   `./domainctl.py --username=benutzer --password=geheim --domain=example.com --host=_acme-challenge --type=TXT --rr="01234abcde" add_record`
 * Entfernen eines betehenden DNS Eintrages:
   `./domainctl.py --username=benutzer --password=geheim --domain=example.com --host=_acme-challenge --type=TXT --rr="01234abcde" add_record --wait`


Parameter
=========

 * --username
 * --password
 * --domain _Domainname_
 * --host _Hostname oder Subdomainname_
 * --type _RR Type_: A, AAAA, MX, CNAME, TXT, SRV
 * --rr _Resource Record_
 * --wait _Auf den Abschluss der DNS Operation warten und erst beenden, wenn der DNS Eintrag erreichbar ist.
