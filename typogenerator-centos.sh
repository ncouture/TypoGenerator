#!/bin/bash
#
# TypoGenerator      Start/Stop TypoGenerator.
#
# chkconfig: 2345 62 38
# description: TypoGenerator XMLRPC Service.
#
# processname: TypoGenerator
#

# Source function library
. /etc/init.d/functions

DAEMON=/home/typogenerator/TypoGenerator/branches/TypoGenerator-CentOS/typogenerator.py
PIDFILE=/home/typogenerator/var/run/typogenerator.pid

RETVAL=0

test -x $DAEMON || {
    echo "Could not find or execute $DAEMON"
    exit 0
}

start() {
	echo -n "Starting TypoGenerator: "
	daemon --user typogenerator $DAEMON
	RETVAL=$?
	echo
	return $RETVAL
}

stop() {
	echo -n "Stopping TypoGenerator: "
	killproc -p $PIDFILE
	RETVAL=$?
	echo
	return $RETVAL
}

case "$1" in
  start)
	start
	;;
  stop)
	stop
	;;

  restart)
	stop
	start
	;;

  *)
	echo "Usage: $0 {start|stop|restart}"
	exit 1
esac

exit $?

