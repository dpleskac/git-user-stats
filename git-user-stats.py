#!/usr/bin/env python3

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
import re
import os
import sys
from subprocess import Popen, call, PIPE, DEVNULL
''' requires pip install iso8601 '''
import iso8601

try:
    # python2
    from urlparse import urlparse
except:
    # python3
    from urllib.parse import urlparse


def user_stats_print(output, date_from, date_to):
    cmd = 'git shortlog -nse'
    if date_from:
        cmd = cmd + ' --after ' + date_from
    if date_to:
        cmd = cmd + ' --before ' + date_to

    with Popen(cmd.split(), stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(' '.join(line.split()[1:]) + '; ' + ''.join(line.split()[0]), file=output)

    if p.returncode != 0:
        print('Failed to get user statistics')
        return False
    return True

def repo_get(repo_str):
    '''
    >>> repo_get('htt://github.com/dpleskac/env')
    Failed to clone a repository htt://github.com/dpleskac/env to a local directory
    False
    >>> repo_get('dexempo/hemenex')
    Local repo directory ...dexempo/hemenex does not exist
    '''
    url = is_url_valid(repo_str)
    if not url.scheme and not url.netloc and url.path:
        ' local repository '
        repo_dir = os.path.join(os.getcwd(), url.path)

    elif url.scheme and url.netloc and url.path:
        ' remote repository '
        cmd = 'git clone ' + repo_str
        if call(cmd.split(), stderr=DEVNULL) != 0:
            print('Failed to clone a repository %s to a local directory' % repo_str)
            return False

        repo_dir = os.path.splitext(os.path.basename(url.path))[0]

    else:
        return None

    if not os.path.isdir(repo_dir):
        print('Local repo directory %s does not exist' % repo_dir)
        return None

    try:
        os.chdir(repo_dir)
    except:
        print('Can\'t cd into repo directory %s' % repo_dir)
        return None

    if call('git status'.split(), stdout=DEVNULL) != 0:
        print('%s is not a proper git repo' % repo_dir)
        return False

    return True

def sanity_check():
    if call('git --version'.split(), stdout=DEVNULL) != 0:
        print('Can\'t execute git binary')
        return False
    else:
        return True

''' input validation '''

def is_url_valid(url):
    try:
        result = urlparse(url)
        return result
    except:
        return False

def repo_type(repo):
    repo_url = is_url_valid(repo)
    if not repo_url:
        msg = "%r is not a valid URL" % repo
        raise argparse.ArgumentTypeError(msg)
    return repo

def parse_date(date):
    '''
    >>> parse_date('2010')
    '2010'
    >>> parse_date('201')
    >>> parse_date('2010-1')
    '2010-1'
    >>> parse_date('2010-1-1')
    '2010-1-1'
    >>> parse_date('2010-13')
    >>> parse_date('2010-11-30')
    '2010-11-30'
    >>> parse_date('2010-11-31')
    >>> parse_date('2010-2-28')
    '2010-2-28'
    >>> parse_date('2010-2-29')
    >>>
    '''
    try:
        iso8601.parse_date(date)
        return date
    except:
        pass
        return None

def date_type(date):
    if parse_date(date) is None:
        msg = "%r is not a valid date" % date
        raise argparse.ArgumentTypeError(msg)
    else:
        return date

def parser():
    parser = argparse.ArgumentParser('print number of user commits contributing to a git repo in a given time period')
    parser.add_argument('-f', type=date_type, help='count commits FROM specific date YYYY[-MM][-DD], ex. 2015-01-30, 2014')
    parser.add_argument('-t', type=date_type, help='count commits TO specific date YYYY[-MM][-DD], ex. 2015-01-30, 2014')
    parser.add_argument('-o', type=argparse.FileType('w'), default=sys.stdout, help='output to a file')
    parser.add_argument('repo', type=repo_type, help='repository\'s URL or directory, ex. http://github.com/dpleskac/env, ./mydir/myrepo')
    args = parser.parse_args()
    return args

def main():
    global args

    args = parser()

    if not sanity_check():
        return

    homedir = os.getcwd()
    if not repo_get(args.repo):
        print('Can\'t get repo')
        return

    if not user_stats_print(args.o, args.f, args.t):
        return


if __name__ == '__main__':
    main()
