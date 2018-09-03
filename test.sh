#!/bin/bash

# unit test(s)
###################
python3 -m doctest -o ELLIPSIS git-user-stats.py || { echo "Unit tests failed"; exit 1; }
echo "Unit tests PASSED"

# functional tests
###################

HOME_DIR=${PWD}
TEST_DIR=$(mktemp -d) && cd ${TEST_DIR} || { echo "Can't create a test directory"; exit 2; }

[ -e golden.output ] && rm golden.output; cat <<EOF > golden.output
Steve Francia <steve.francia@gmail.com>; 125
Richard Bateman <taxilian@gmail.com>; 31
Ben Loveridge <bloveridge@gmail.com>; 29
Ben Loveridge <bloveridge@movenetworks.com>; 14
spf13 <steve.francia@gmail.com>; 10
Richard Bateman <taxilian@fb.com>; 3
Scott <munkt0n@gmail.com>; 3
Ramon Marco Navarro <ramonmaruko@gmail.com>; 2
Dusty Leary <dleary@gmail.com>; 1
Steve Francia <sfrancia@theopenskyproject.com>; 1
EOF

# test remote repo
TST_CMD="${HOME_DIR}/git-user-stats.py -f 2000 -t 2011 https://github.com/spf13/spf13-vim.git"

${TST_CMD} | cmp - golden.output || { echo "Test 1 output differs from golden output"; exit 3; }

echo "Functional test 1 PASSED"

# test local repo
TST_CMD="${HOME_DIR}/git-user-stats.py -f 2000 -t 2011 spf13-vim"

${TST_CMD} | cmp - golden.output || { echo "Test 2 output differs from golden output"; exit 4; }

echo "Functional test 2 PASSED"

# test output option 
TST_CMD="${HOME_DIR}/git-user-stats.py -f 2000 -t 2011 -o user-stat.txt spf13-vim"

${TST_CMD} && cmp user-stat.txt golden.output || { echo "Test 3 output differs from golden output"; exit 5; }

rm user-stat.txt

echo "Functional test 3 PASSED"

# cleanup
cd ${HOME_DIR} && rm -rf ${TEST_DIR}
