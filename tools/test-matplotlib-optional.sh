#!/bin/bash

set -e

log_file=tmp/test-matplotlib-optional.log
out_file=tmp/test-matplotlib-optional.out
pid_file=tmp/test-matplotlib-optional.pid

kill-orgviz(){
    if [ -n "$pid" ]
    then
        echo "Killing server (pid=$pid)." >> $log_file
        kill $pid
    fi
}
trap kill-orgviz EXIT

echo "############### Test: OrgViz can run wihout matplotlib ################"

mkdir -p $(dirname $log_file)
rm -f $log_file
echo "Make sure matplotlib is not importable" >> $log_file
printf .
if python -c 'import matplotlib' 2> /dev/null
then
    echo "This environment has matplotlib"
    exit 1
fi

printf .
for port in {7000..8000}
do
    echo "Starting server using port $port" >> $log_file
    orgviz sample --port $port 2> $out_file &
    pid=$!
    echo $pid > $pid_file
    url="http://127.0.0.1:$port"
    for _ in {1..30}
    do
        if grep "Running on $url/" $out_file > /dev/null
        then
            echo "Process Started." >> $log_file
            break
        fi
        sleep 0.1
    done
    if grep "^Traceback " $out_file > /dev/null
    then
        echo "Failed to start server using port $port." >> $log_file
    else
        break
    fi
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

echo "Requesting $url/orgviz." >> $log_file
printf .
wget $url/orgviz -O /dev/null --output-file /dev/null

echo "OK"
