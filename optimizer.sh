PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

ENV=caliope
BASE=$(echo $PWD | awk -F'caliope_server_el_cid' '{print $1}')
PYTHON=${HOME}/.virtualenvs/${ENV}/bin/python
DAEMON=./src/cid/utils/jsOptimizerProcess.py
DAEMON_ARGS="-c conf/caliope_server.json"
RUNDIR=./var
PIDFILE=$RUNDIR/optimizer-server.pid
DESC="Optimizer Server"
NAME=Optimizer



export PYTHONPATH=${BASE}/caliope_server_el_cid/src


test -x $DAEMON || exit 0
  

case "$1" in
  start)
        echo -n "Starting $DESC: "
        mkdir -p $RUNDIR
        touch $PIDFILE


        if start-stop-daemon --start --quiet --background --umask 002 --pidfile $PIDFILE --chdir $PWD --exec  $PYTHON $PWD/$DAEMON -- $DAEMON_ARGS
        then
                PID=$(ps  ax|grep ${DAEMON}|grep -v grep|awk '{ print $1}')
                echo $PID >  $PIDFILE
                echo "$NAME."
        else
                echo "failed"
        fi
        ;;
  stop)
        echo -n "Stopping $DESC: "
        if start-stop-daemon --stop --retry forever/TERM/1 --quiet --oknodo --pidfile $PIDFILE --exec  $PYTHON $PWD/$DAEMON
        then
                echo "$NAME."
        else
                echo "failed"
        fi
        rm -f $PIDFILE
        sleep 1
        ;;

  restart|force-reload)
        ${0} stop
        ${0} start
        ;;

  status)
        echo -n "$DESC is "
        if start-stop-daemon --stop --quiet --signal 0 --name ${NAME} --pidfile ${PIDFILE}
        then
                echo "running"
        else
                echo "not running"
                exit 1
        fi
        ;;

  *)
        echo "Usage: /etc/init.d/$NAME {start|stop|restart|force-reload|status}" >&2
        exit 1
        ;;
esac

exit 0
