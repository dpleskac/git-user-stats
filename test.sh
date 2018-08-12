#!/bin/bash

HOME_DIR=${PWD}
TEST_DIR=$(mktemp -d) && cd ${TEST_DIR} || { echo "Can't create a test directory"; exit 1; }

TST_CMD="${HOME_DIR}/git-user-stats.py -f 2000 -t 2011 https://github.com/spf13/spf13-vim.git"

[ -e golden.putput ] && rm golden.output; cat <<EOF >golden.output
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

${TST_CMD} | cmp - golden.output || { echo "Test output differs from golden output"; exit 2; }

cd - && rm -rf ${TEST_DIR}

echo "Test PASSED"
