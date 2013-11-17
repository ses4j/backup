
Scott's Backup Script
=====================

My personal backup script, uses a tower-of-hanoi slot alternation to keep old backups.

INSTALLATION and CONFIGURATION
------------------------------

First, install prerequisites:
 * Python (tested with version 2.4)
 * If Win32 for Python is installed, it'll use that a bit too.

Put all backup_script files into some directory, say C:\backup_script.

Copy backup.ini-template file to backup.ini.

Edit backup.ini; this file controls the backup by telling it what to copy and where.

The first line is the destination root directory.  Good examples are:

C:\backup (to just backup to the local hard drive)
G:\backup\tsvey (to backup to USB drive at G:)

Then the next lines are the directories you want to back up.  The script will copy everything
under those directories to your backup location.  If there's a comma in the line, the second
thing is the folder to copy it into under the destionation root directory (otherwise it defaults
to whatever the source dir name is)... The default backup.ini-template would do this:

E:\etc --> c:\temp\backup\slot0\etcetera
E:\misc\PGP -> c:\temp\backup\slot0\PGP

and the second time it runs, it'll copy to slot1.  Then slot0, slot2, slot 0, slot 1, and so on in
hanoi pattern.

RUNNING
--------

Once your backup.ini file is set up, just run

    backup_script.py

EXTRA SETTINGS
--------------

If you want, you can open the backup_script.py and muck with
these configuration settings too:

NUMBER_OF_SLOTS = 10
EXCLUDE_DIRS = ' "Temporary Internet Files" "Cache" "Recent" "Cookies" "iPod Photo Cache" "MachineKeys" ".svn" "CVS" '
EXCLUDE_FILES = ' ~$*.* *.bak *.tmp index.dat usrclass.dat* ntuser.dat* *.lock *.swp *.pyc *.obj *.pch *.ilk *.pdb *.a *.lib *.exp'
