#!/bin/sh
set -eu
exec /usr/bin/gcc -specs=/opt/musl-sysroot/musl-gcc.specs \
  -L/opt/musl-sysroot/usr/lib -L/opt/musl-sysroot/lib \
  -Wl,-rpath-link,/opt/musl-sysroot/lib "$@"
