'''
Zadani:

Napis programek v Pythonu, ktery bude mit jako vstup cestu ke git repozitari a bude poskytovat agregace (pocty commitu) pro jednotlive uzivatele, kteri do repozitare prispivaji.

Pozadavky:

* skript se bude volat s jednim povinnym parametrem "repositar"
* bude mozne specifikovat rozsah agregace pomoci prepinacu a to nasledovne
    -f (from date) - prvni den, ktery spada do intervalu
    -t (to date) - posledni den, ktery spada do intervalu
    format data: YYYY-MM-DD (ISO 8601)
  oba prepinace jsou volitelne - pokud se nespecifikuji, bude se agregovat
  pres celou historii repositare, jinak se bude agregovat dle zvolenych omezeni
  (napr. pokud bude jenom -f budou se scitat vsechny commity od zvoleneho data
  az do konce gitove historie, analogicky pro -t)
* bude mozne specifikovat vystupni soubor pomoci parametru -o <vystupni soubor>,
  pokud prepinac -o nebude uveden, pouzije se standardni vystup (STDOUT)
* je potreba provest validaci vstupnich parametru - pro chybne zadane parametry
  skript vypise chybove hlaseni, z nehoz je mozne poznat, co je spatne
* bude existovat akceptacni test pro skript, ktery lze spustit a ktery proveri
  zakladni funkcionalitu skriptu (napr. skript, ktery zavola ./git-statistics.py
  nad znamym repositarem a proveri, ze jsou ve vystupu ocekavane hodnoty)
* budou existovat jednotkove testy
* pri odevzdani bychom chteli videt demo celeho reseni
* zdrojove kody budou verzovane v GIT repu (s tim, ze je pro nas zajimave
  i jak kod postupne vznikal)

Priklad invokace:

./git-statistics.py -o statistics.txt -f 2017-06-01 https://github.com/torvalds/linux.git

* zapise vysledky do souboru statistics.txt, agregovat se bude od prvniho cervna 2017 az do konce historie repozitare, pouzije se repozitar https://github.com/torvalds/linux.git

Priklad vystupu:

Jan Novak <jan.novak@example.com>; 345
Helena Vondrackova <helena.vondrackova@otherdomain.com>; 1046 
'''

import argparse
try:
    # python2
    from urlparse import urlparse
except:
    # python3
    from urllib.parse import urlparse


def is_url_valid(url):
    try:
        result = urlparse(url)
        return result
    except:
        return False

def is_local_repo(url):
    return not url.netloc and url.path

def is_remote_repo(url):
    return url.scheme and url.netloc and url.path

def repo_type(repo):
    print('testing repo type', repo)
    repo_url = is_url_valid(repo)
    if not repo_url:
        msg = "%r is not a valid repository" % repo
        raise argparse.ArgumentTypeError(msg)
    if is_local_repo(repo_url) or is_remote_repo(repo_url):
        return repo

def parser():
    parser = argparse.ArgumentParser('print number of user commits contributing to a git repo in a given time period')
    parser.add_argument('-f', help='count commits FROM specific date YYYY[-MM][-DD], ex. 2015-01-30, 2014')
    parser.add_argument('-t', help='count commits TO specific date YYYY[-MM][-DD], ex. 2015-01-30, 2014')
    parser.add_argument('-o', type=argparse.FileType('w'), help='output to a file')
    parser.add_argument('repo', type=repo_type, help='repository\'s URL or directory, ex. http://github.com/dpleskac/env, ./mydir/myrepo')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    global args
    args = parser()
