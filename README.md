Bawue.Net DNS API client
========================

Dieser Client erlaubt es, seine beim [Bawue.Net](https://www.bawue.net/) gehosteten Domains von der Kommandozeile aus zu administrieren.
Somit kann auf einfache Weite ein Let'sEncrypt Zertifikat mit der DNS-01 Challenge erzeugt werden.

Installation
------------

Am einfachsten direkt mit PIP:

`pip install 'git+https://github.com/bawuenet/domainctl'`


Beispielaufruf
--------------

 * Anzeigen aller Domains:
   `./domainctl.py --username=benutzer --password=geheim list_domains`
 * Anzeigen aller DNS Einträge einer Domain:
   `./domainctl.py --username=benutzer --password=geheim --domain=example.com list_domains`
 * Hinzufügen eines neuen DNS Eintrages:
   `./domainctl.py --username=benutzer --password=geheim --domain=example.com --host=_acme-challenge --type=TXT --rr="01234abcde" add_record`
 * Entfernen eines betehenden DNS Eintrages und warten, dass das Update der Zone erfolgt ist:
   `./domainctl.py --username=benutzer --password=geheim --domain=example.com --host=_acme-challenge --type=TXT --rr="01234abcde" remove_record --wait`


Parameter
---------

 * Username und Passwort entweder:
   * --credentials als Datei mit den Zugangsdaten
   * --username und --password
 * --domain _Domainname_
 * --host _Hostname oder Subdomainname_
 * --type _RR Type_: A, AAAA, MX, CNAME, TXT, SRV
 * --rr _Resource Record_
 * --wait _Auf den Abschluss der DNS Operation warten und erst beenden, wenn der DNS Eintrag erreichbar ist._

Credential File
---------------

Eine `.ini` Datei, die den Usernamen und das Passwort enthält, damit dieses nicht als Kommandozeilen-
Parameter übergeben werden muss:

```INI
[bawue]
username=benutzer
password=geheim
```

Hinweise
--------

 * TXT Records
   * Diese sollten normalerweise von doppelten Anführungszeichen (`"`) umschlossen sein.
   * An der Kommandozeile am besten als `'"Dies ist ein Text"'` in einfachen Anführungszeichen (`'`) umschliessen.
 * CNAME Records
   * Der Ressource Record sollte immer auf einen "." enden. (Trailing dot) 

Ansible
-------

Dieses Git-Repository kann auch als Ansible Collection benutzt werden:

```
mkdir -p ~.ansible/collections/ansible_collections/bawuenet
cd ~.ansible/collections/ansible_collections/bawuenet
git clone https://github.com/bawuenet/domainctl.git
# oder
git clone git@github.com:bawuenet/domainctl.git
cd
ansible-doc bawuenet.domainctl.bwnet_domains_info
```

Diese Collection `bawuenet.domainctl` definiert die Modulen:

* `bwnet_domains_info`, um Domänen eines bestimmten Benutzers aufzulisten
* `bwnet_records_info`, um Records in einer Domäne aufzulisten
* `bwnet_record`, um ein Record aus einer Domäne zu löschen oder hinzuzufügen

Es sind auch zwei Playbooks vorhanden, um die Benutzung zu erläutern.
