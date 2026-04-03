#!/bin/bash
for i in 101 108 109 110 130 211; do
    echo -n "CT $i: "
    pct config $i 2>/dev/null | grep hostname || echo "not found"
done
