#!/bin/bash

rm -r public
mkdir public
mkdir public/static

# Copy non-css stuff untouched
shopt -s extglob
cp static/*.!(css) public/static/

# Take checksum of stylesheet and embed in filename
hash=$(sha1sum < static/style.css | head -c 8)
cp static/style.css public/static/style.$hash.css
