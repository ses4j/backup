Scott's Backup Script
=====================

My personal Windows backup script, uses a 
[tower-of-hanoi slot alternation](http://en.wikipedia.org/wiki/Backup_rotation_scheme#Tower_of_Hanoi) 
to keep old backups.  Nothing complicated; I like my backups reliable and easy to recover, so this script
simply copies (via robocopy.exe) the contents of a list of directories to another target directory
(presumably an external or network drive.  No incremental backups, no proprietary formats, no compression
(unless you set up compression in the Windows filesystem yourself), nothing that adds any complexity to
recovering files.

INSTALLATION and CONFIGURATION
------------------------------

First, install prerequisites:
 * Python (tested with version 2.4-2.7)
 * If Win32 for Python is installed, it'll use that a bit too.

Put all backup_script files into some directory, say C:\backup_script.

Copy backup.ini-template file to backup.ini.

Edit backup.ini; this file controls the backup by telling it what to copy and where.

BACKUP_ROOT defines the destination root directory.  Good examples are:

    BACKUP_ROOT=G:\backup

Next, setup the BACKUP_PATHS, the directories you want to back up.  The script will copy everything
under those directories to your backup location.  Separate paths by semicolon (;), if there's a pipe (|)
in the line, the second thing is the folder to copy it into under the destination root directory
(otherwise it defaults to whatever the source dir name is):

    BACKUP_ROOT=G:\backup
    BACKUP_PATHS=c:\misc;C:\pix\favorites|pix-favorites

would copy like so:

    C:\misc --> G:\backup\slot0\misc
    C:\pix\favorites --> G:\backup\slot0\pix-favorites

and the second time it runs, it'll copy to slot1.  Then slot0, slot2, slot 0, slot 1, and so on in
hanoi pattern.

You can also set a SINGLESLOT_BACKUP_PATHS if you have large directories that you don't care about history
on.  It will copy these paths to the "single" directory, instead of a slot.

RUNNING
--------

Once your backup.ini file is set up, just run

    backup_script.py

EXTRA SETTINGS
--------------

If you want, you can also muck with these configuration settings too:

    NUMBER_OF_SLOTS = 3
    EXCLUDE_DIRS = ' "Temporary Internet Files" "Cache" "Recent" "Cookies" "iPod Photo Cache" "MachineKeys" ".svn" "CVS" '
    EXCLUDE_FILES = ' ~$*.* *.bak *.tmp index.dat usrclass.dat* ntuser.dat* *.lock *.swp *.pyc *.obj *.pch *.ilk *.pdb *.a *.lib *.exp'
