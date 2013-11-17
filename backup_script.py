"""
Simple backup script that copies a selected list of directories to
a slot on another drive/path.  It chooses a slot based on the tower-of-hanoi
strategy for keeping new and old copies available.

(c) 2007-2013 Scott Stafford
Distributed under the MIT License (see LICENSE file)
"""

import ConfigParser
import time,os,shutil,sys,traceback

try:
    import win32gui
except ImportError:
    win32gui = None
try:
    import win32api,win32con
except ImportError:
    win32api = None
    win32con = None

from winsound import *

import hanoi
import oslockedaction

# types of supported backups
SON_FATHER_GRANDFATHER = 'SON_FATHER_GRANDFATHER'
TOWER_OF_HANOI = 'TOWER_OF_HANOI'

config = ConfigParser.SafeConfigParser()
config.read(['backup.ini'])

NUMBER_OF_SLOTS = config.getint('backup','NUMBER_OF_SLOTS')
EXCLUDE_DIRS = config.get('backup','EXCLUDE_DIRS').split(';')
EXCLUDE_FILES = config.get('backup','EXCLUDE_FILES').split(';')

BACKUP_ROOT = config.get("backup","BACKUP_ROOT")
backup_paths = config.get("backup","BACKUP_PATHS")
DIRS_TO_MIRROR=[]
for path in backup_paths.split(';'):
    s = path.split('|')
    source_path = s[0]
    if len(s)==1:
        target_path = os.path.split(s[0])[-1]
    elif len(s)==2:
        target_path = s[1]
    else:
        raise ValueError("At most 1 pipe (|) per line: %s"%(str(path)))
        
    if not os.path.exists(source_path):
        raise ValueError("Path %s does not exist." % source_path)
    DIRS_TO_MIRROR.append((source_path, target_path))

print "BACKUP_ROOT:",BACKUP_ROOT
print "DIRS",DIRS_TO_MIRROR

class RoboError(RuntimeError):
    def __init__(self, why, errorlevel):
        self.errorlevel = errorlevel
        RuntimeError.__init__(self, why + " errorlevel=" + str(errorlevel))
class DryRunException(RuntimeError):
    pass
    
def run_a_backup(source_dir, dest_dir, dry_run = False):
    #~ REM See the robocopy documentation for what each command does.
    #~ REM /COPY:DAT :: COPY file data, attributes, and timestamps
    #~ REM /COPYALL :: COPY ALL file info
    #~ REM /B :: copy files in Backup mode.
    #~ REM /MIR :: MIRror a directory tree
    #~ REM /L :: Just list the info, don't actually do it
    what_to_copy = " /COPY:DAT /MIR "

    #~ REM Exclude some files and directories that include transient data
    #~ REM that doesn't need to be copied.
    if len(EXCLUDE_DIRS)>0:
        exclude_dirs=' /XD ' + "".join(['"%s" '%dir for dir in EXCLUDE_DIRS])
    else:
        exclude_dirs=''
    if len(EXCLUDE_FILES)>0:
        exclude_files=" /XF " + " ".join(EXCLUDE_FILES)
    else:
        exclude_files=''

    #~ REM Refer to the robocopy documentation for more details.
    #~ REM /R:n :: number of Retries
    #~ REM /W:n :: Wait time between retries
    #~ REM /LOG :: Output log file
    #~ REM /NFL :: No file logging
    #~ REM /NDL :: No dir logging
    #~ REM SET options=/R:0 /W:0 /LOG+:%log_fname% /NFL /NDL
    log_filename = "backuplog-"+time.strftime("%Y-%m-%d-%Hh") +".log"
    #~ print log_filename
    options=' /LOG+:%s /NFL /TEE /ETA '%log_filename

    #~ REM Execute the command based on all of our parameters
    cmd='ROBOCOPY "%(source_dir)s" "%(dest_dir)s" %(what_to_copy)s %(options)s %(exclude_dirs)s %(exclude_files)s '%locals()
    #~ print cmd

    if dry_run:
       print "Would have executed: " + cmd
       raise DryRunException()
              
    if not os.path.exists(dest_dir):
        #~ print "first, creating the directory..." + dest_dir
        errorlevel = os.system(cmd + " /CREATE")
        if errorlevel > 1:
            raise RoboError( "Problem!", errorlevel )

    #~ print cmd
    errorlevel = os.system(cmd)
    if errorlevel > 3:
        raise RoboError( "Problem!", errorlevel )

    log_directory = BACKUP_ROOT + '\\logs'

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    shutil.copy2(log_filename, log_directory)


class CounterFile:
    def __init__(self):
        self.path = BACKUP_ROOT + os.sep + "scottbackup_hanoi_counter.cfg"

        if not os.path.exists(self.path):
            print "First run!  Initializing backup root %s" % BACKUP_ROOT
            print self.path
            os.makedirs(os.path.dirname(self.path))
            f = open(self.path,'w')
            f.write("0")
            f.close()
        if win32api is not None:
            win32api.SetFileAttributes(self.path,win32con.FILE_ATTRIBUTE_HIDDEN)
        f = open(self.path,'r')
        self.count = int(f.read())
        assert self.count>=0
        f.close()

    def incrementAndWrite(self):
        if win32api is not None:
            win32api.SetFileAttributes(self.path, win32con.FILE_ATTRIBUTE_NORMAL)
        f = open(self.path, 'w')
        f.write(str(self.count + 1))
        f.close()
        if win32api is not None:
            win32api.SetFileAttributes(self.path,win32con.FILE_ATTRIBUTE_HIDDEN)

def _backup(backup_mode = TOWER_OF_HANOI):
    errors = []

    counterFile = CounterFile()
    if backup_mode == SON_FATHER_GRANDFATHER:
        tstruct = time.localtime()
        if tstruct.tm_mday == 1:
            dest_dir_part = "monthly"
        elif tstruct.tm_wday == 0:
            dest_dir_part = "weekly"
        else:
            dest_dir_part = "daily"
    elif backup_mode == TOWER_OF_HANOI:
        #~ days_since_any_epoch = time.time() / 60.0 / 60.0 / 24.0
        days_since_any_epoch = counterFile.count
        print "BACKUP NUMBER ",days_since_any_epoch
        numDisks = NUMBER_OF_SLOTS
        hanoi_slot = hanoi.get_current_hanoi_slot(days_since_any_epoch, numDisks = numDisks)
        dest_dir_part = "slot%d"%hanoi_slot
    else:
        dest_dir_part = "here"

    backup_base_path = "%s\\%s"%(BACKUP_ROOT, dest_dir_part)

    if not os.path.exists(backup_base_path):
        os.makedirs(backup_base_path)
    shutil.copy2(__file__, backup_base_path)
    shutil.copy2('backup.ini', backup_base_path)

    for (path,dest_dir_end) in DIRS_TO_MIRROR:

        target_path = '%s\\%s'%(backup_base_path, dest_dir_end)
        try:
            run_a_backup(path, target_path)
        except RoboError, e:
            errors.append("ERROR %d: %s -> %s"%(e.errorlevel,path,target_path))
            print e.errorlevel
        except DryRunException, e:
            errors.append("Nothing happened - dry run.")

    def announce(msg, title, icon):
        print title
        print "  -",msg
        if win32gui:
            win32gui.MessageBox(0, msg, title, icon)

    if len(errors)==0:
        counterFile.incrementAndWrite()
        announce( "Backup script completed properly.", "Scott's Backup script", 0)
    else:
        announce( "Backup script had errors:\r\n%s"%"\r\n".join(errors), "Scott's Backup script Error!", MB_ICONEXCLAMATION)

def _restore():
    what_dir_to_restore = 'scott'

    source_dir = r'F:\backup\mensch\slot2' + os.sep + what_dir_to_restore
    dest_dir = r'C:' + os.sep + what_dir_to_restore
    #~ dest_dir = r'C:\Documents and Settings\Administrator\My Documents\My Music' + os.sep + what_dir_to_restore

    #~ REM See the robocopy documentation for what each command does.
    #~ REM /COPY:DAT :: COPY file data, attributes, and timestamps
    #~ REM /COPYALL :: COPY ALL file info
    #~ REM /B :: copy files in Backup mode.
    #~ REM /MIR :: MIRror a directory tree
    #~ REM /L :: Just list the info, don't actually do it
    what_to_copy = " /COPY:DAT /MIR "

    #~ REM Exclude some files and directories that include transient data
    #~ REM that doesn't need to be copied.
    exclude_dirs=' '
    exclude_files=' '

    #~ REM Refer to the robocopy documentation for more details.
    #~ REM /R:n :: number of Retries
    #~ REM /W:n :: Wait time between retries
    #~ REM /LOG :: Output log file
    #~ REM /NFL :: No file logging
    #~ REM /NDL :: No dir logging
    #~ REM SET options=/R:0 /W:0 /LOG+:%log_fname% /NFL /NDL
    log_filename = "backuplog-"+time.strftime("%Y-%m-%d-%Hh") +".log"
    #~ print log_filename
    options=' /LOG+:%s /ETA '%log_filename

    #~ REM Execute the command based on all of our parameters
    cmd='ROBOCOPY "%(source_dir)s" "%(dest_dir)s" %(what_to_copy)s %(options)s %(exclude_dirs)s %(exclude_files)s '%locals()
    #~ print cmd

    #~ if not os.path.exists(dest_dir):
        #~ errorlevel = os.system(cmd + " /CREATE")
        #~ if errorlevel > 1:
            #~ raise RoboError( "Problem!", errorlevel )

    print cmd
    errorlevel = os.system(cmd)
    if errorlevel > 3:
        raise RoboError( "Problem!", errorlevel )

    #~ log_directory = BACKUP_ROOT + '\\logs'

    #~ if not os.path.exists(log_directory):
        #~ os.makedirs(log_directory)
    #~ shutil.copy2(log_filename, log_directory)


def backup():
    try:
        oslockedaction.OSLockedAction(target=_backup, timeoutDelay = 0.0, DEBUG = False)
        sys.exit(0) 
    except:
        traceback.print_exc()

        print "Backup failed with errors."
        if win32gui:
            win32gui.MessageBox(0, "Backup script had errors...", "Scott's Backup script Error!", MB_ICONEXCLAMATION)
        sys.exit(1) 

def restore():
    try:
        oslockedaction.OSLockedAction(target=_restore, timeoutDelay = 0.0, DEBUG = False)
        sys.exit(0) 
    except:
        traceback.print_exc()
        if win32gui:
            win32gui.MessageBox(0, "Backup script had errors...", "Scott's Backup script Error!", MB_ICONEXCLAMATION)
        sys.exit(1) 


if __name__=='__main__':
    backup()

