#!/bin/bash

set -e

log_file=tmp/test-matplotlib-optional.log
pid_file=tmp/test-matplotlib-optional.pid

echo "############### Test: OrgViz can run wihout matplotlib ################"

mkdir -p $(dirname $log_file)
printf .
if python -c 'import matplotlib' 2> /dev/null
then
    echo "This environment has matplotlib"
    exit 1
fi

printf .
for port in {7000..8000}
do
    python -m orgviz.cli sample --port $port 2> $log_file &
    pid=$!
    echo $pid > $pid_file
    sleep 1
    url="http://127.0.0.1:$port"
    if grep "Running on $url/" $log_file > /dev/null
    then
        break
    fi
    kill $pid
    port=""
done


printf .
if ps --pid $pid > /dev/null
then :
else
    echo "Failed to start server."
    exit 1
fi

printf .
if [ -z "$port" ]
then
    echo "Failed to start server."
    exit 1
fi

printf .
wget $url/orgviz -O /dev/null --output-file /dev/null
printf .
kill $pid
echo "OK"
