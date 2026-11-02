#!/bin/sh

if git push "$@"; then
    printf '%s\n' "Push completado correctamente."
else
    result=$?
    exit "$result"
fi
