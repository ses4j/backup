class LockFileExists(RuntimeError): pass

class OSLockedAction:
    def __init__(self, target, args = (), kwargs = {}, lockfile = None, timeoutDelay = 7.0, retryPeriod = 0.1, DEBUG = False):
        """
        To use, just wrap your python call with an OSLockedAction() constructor.  Instead of:
        >>> time.sleep(5.0)
        Do:
        >>> OSLockedAction(target = time.sleep, args = (5.0,), lockfile="C:\\myLockFile.lock")
        Nobody else using the same lockfile will be able to run at the same time.

        lockfile will default to the script's name with .lock at the end
        timeoutDelay is a float in seconds.
            if timeoutDelay is None, it will never timeout if the lockfile exists.
                It will wait forever if the lockfile contines to exist.
            If it is >0, it will just try to remove the lockfile after timeoutDelay seconds and do 'action()' anyway.
            If it is ==0, it will try once and if lockfile exists, it will give up and throw LockFileExists.
        retryPeriod is a float in seconds.
        description will be dumped into the lockfile, so you can see what wrote it.

        Author: Scott Stafford 2007
        """
        import time,os,sys
        if lockfile is None:
            lockfile = sys.argv[0] + '.lock'
        lockfile = os.path.abspath(lockfile)
        print lockfile

        ### Block if lockfile exists until it's gone...
        f = None

        if timeoutDelay is not None:
            end_time = time.clock() + timeoutDelay*2
            start_deleting_time = time.clock() + timeoutDelay

        try:
            #~ if DEBUG:
                #~ print "lockfile", lockfile, " exists=",os.path.exists(lockfile)
            while 1:
                if timeoutDelay is not None and timeoutDelay != 0.0 and start_deleting_time < time.clock(): # timed out, it must be stale... (i hope)  so remove it.
                    try:
                        if DEBUG: print  >>sys.stderr, "TRYING TO REMOVE...",
                        os.remove(lockfile)
                        if DEBUG: print  >>sys.stderr, "REMOVED STALE LOCK",
                    except OSError:
                        time.sleep(retryPeriod)
                try:
                    if DEBUG: print  >>sys.stderr, "TRYING TO OPEN...",
                    f = os.open(lockfile,os.O_RDWR | os.O_CREAT | os.O_EXCL)
                    os.write(f,str(__file__) + " made this, called from " + sys.argv[0])
                    if DEBUG: print  >>sys.stderr, "OPENED"
                    break
                except OSError:
                    if DEBUG: print  >>sys.stderr, "SLEEPING..."
                    time.sleep(retryPeriod)
                if f or timeoutDelay == 0.0 or (timeoutDelay is not None and end_time > time.clock()):
                    break
            if not f:
                print >>sys.stderr, """-=-
FAIL: OSLockedAction can't acquire directory lock, because
%s
was not cleaned up.  Delete it manually if the process is finished.
-=-
"""%(lockfile)
                raise LockFileExists()

            target(*args, **kwargs)
        finally:
            ### Release the lock
            if f:
                if DEBUG:
                    print  >>sys.stderr, "RELEASING...",
                os.close(f)
                os.remove(lockfile)
                if DEBUG:
                    print  >>sys.stderr, "RELEASED"


def example():
    import time
    def action(t, msg):
        print "I'm going to print a message...",
        time.sleep(t);
        print msg
    ola = OSLockedAction(target = action, args = (5.0,), kwargs = {'msg': 'This is my message!'}, DEBUG=True)

if __name__=='__main__':
    example()
