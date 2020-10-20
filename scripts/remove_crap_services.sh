#!/bin/sh

for SVC in stat_points statisticsservice datacenter \
           smartcontroller plugincenter \
           plugin_start_script.sh cp_preinstall_plugins.sh; do
   # rm -f $FSDIR/etc/rc.d/[SK]*$SVC
   echo $FSDIR/etc/rc.d/[SK]*$SVC
done
