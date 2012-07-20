#! /bin/sh

### BEGIN INIT INFO
# Provides:		TypoGenerator
# Required-Start:	$remote_fs $syslog
# Required-Stop:	$remote_fs $syslog
# Default-Start:	2 3 4 5
# Default-Stop:		1
# Short-Description:	TypoGenerator XMLRPC Service
### END INIT INFO

set -e

DAEMON=/home/typogenerator/TypoGenerator/trunk/typogenerator.py
PIDFILE=/home/typogenerator/var/run/typogenerator.pid

test -x $DAEMON || {
    log_daemon_msg "Could not find or execute $DAEMON"
    exit 0
}

. /lib/lsb/init-functions

# Are we running from init?
run_by_init() {
    ([ "$previous" ] && [ "$runlevel" ]) || [ "$runlevel" = S ]
}

export PATH="${PATH:+$PATH:}/usr/sbin:/sbin"

case "$1" in
  start)
	log_daemon_msg "Starting the TypoGenerator XMLRPC service" "TypoGenerator"
	if start-stop-daemon --chuid typo3 --start --quiet --oknodo --pidfile $PIDFILE --exec $DAEMON; then
	    log_end_msg 0
	else
	    log_end_msg 1
	fi
	;;
  stop)
	log_daemon_msg "Stopping TypoGenerator XMLRPC service" "TypoGenerator"
	if start-stop-daemon --chuid typo3 --stop --quiet --oknodo --pidfile $PIDFILE; then
	    log_end_msg 0
	else
	    log_end_msg 1
	fi
	;;

  restart)
	log_daemon_msg "Restarting TypoGenerator XMLRPC service" "TypoGenerator"
	start-stop-daemon --chuid typo3 --stop --quiet --oknodo --retry 30 --pidfile $PIDFILE
	if start-stop-daemon --chuid typo3 --start --quiet --oknodo --pidfile $PIDFILE --exec $DAEMON; then
	    log_end_msg 0
	else
	    log_end_msg 1
	fi
	;;

  *)
	log_action_msg "Usage: /etc/init.d/typogenerator {start|stop|restart}"
	exit 1
esac

exit 0
