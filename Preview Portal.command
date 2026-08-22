#!/bin/zsh
set -e
cd "${0:A:h}"
open "http://127.0.0.1:8766/"
python3 -m http.server 8766 --bind 127.0.0.1
