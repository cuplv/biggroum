#!/bin/bash

# Use:  In the .muse.toml specify:
# ```
# customTools = "https://scripts.muse.dev/scripts/shellcheck.sh"
# ```
#dir=$1
#commit=$2
cmd=$3
shift
shift
shift

if [[ "$cmd" = "run" ]] ; then
    jsonout=$(find . -executable -print0 -name '*.sh' | xargs shellcheck -S error -f json "$@")
    if [[ ! ( "[]" = "$jsonout" ) ]] ; then
        echo "$jsonout" | jq --arg type ShellCheck 'map (. + {type: $type})'
    else
        echo "$jsonout"
    fi
fi

if [[ "$cmd" = "applicable" ]] ; then
    echo "true"
fi

if [[ "$cmd" = "version" ]] ; then
    echo "1"
fi
