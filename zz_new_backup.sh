#!/bin/sh

#################################################################
# Adapted from Zimbra Wiki					#
# Zimbra Backup and Restore "hot". [By Richardson Lima]		#
#################################################################
#								#
# Modifications by Gary Atkinson - Oct 2011			#
#								#
#################################################################

# script must be ran as root

#setup some variables
DAY=`date +"%a"`
TODAY=`date +"%m-%d-%Y"`
YESTERDAY=`date -d '1 day ago' +'%m-%d-%Y'`
DAYBEFORE=`date -d '2 day ago' +'%m-%d-%Y'`
DAYNUMBER=`date +"%d"`

REMOVEDAYBEFORE=/media/backup/opt_zimbra.$DAYBEFORE
TODAYSDIR=/media/backup/opt_zimbra.$TODAY
YESTERDAYDIR=/media/backup/opt_zimbra.$YESTERDAY

BACKUPTOUSB="Sun"

BACKUP=/media/backup

ZHOME=/opt/zimbra
ZBACKUP=/media/backup/zimbra_files/backup/mailbox
ZBACKUP_SCRIPT=/opt/zimbra_backup/scripts
ZBACKUPLOGDIR=/opt/zimbra_backup/logs
LOGFILE=$ZBACKUPLOGDIR/backup.log

configdir_cs1=$BACKUP/cs1_linux_config_files
configdir_cse10=$BACKUP/cse10_linux_config_files

#write to the log file
log(){
    message="$@"
#    echo $message
    echo $message >>$LOGFILE
}

#create log file if missing
if [ ! -f $LOGFILE ]; then
#echo "File not found!"
   touch $LOGFILE
#echo $LOGFILE
   chmod 646 $LOGFILE
fi

log ""
log ""
log "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
log "Start time of backup is... `(date +%c)`"
log ""
before="$(date +%s)"


log "Generating Mailbox backup files ..."

su - zimbra -c $ZBACKUP_SCRIPT/BackupAllAccounts.sh


log "Generating Mailbox backup files ...Done"

log "Sending files to backup drive ..."
# Stop Zimbra Services
su - zimbra -c"/opt/zimbra/bin/zmcontrol stop"
sleep 15

# Kill any orphaned Zimbra processes
kill -9 `ps -u zimbra -o "pid="`

# Sync to backup directory


#echo $REMOVEDAYBEFORE
if [ -d $REMOVEDAYBEFORE ]; then
   log "Directory $REMOVEDAYBEFORE is being removed"
   rm -rf $REMOVEDAYBEFORE
fi
log "Creating directory $TODAYSDIR..."
#rsync -aHK --delete --exclude log/ /opt/zimbra/ $TODAYSDIR/zimbra
#rsync -aHK --delete --exclude log/ /opt/zimbra $TODAYSDIR
rsync -aHK --delete $ZHOME $TODAYSDIR

#rsync -aHK --delete --exclude log/ /opt/zimbra/ /media/backup/zimbra

# Restart Zimbra Services
su - zimbra -c "/opt/zimbra/bin/zmcontrol start"
sleep 15


# copies backup of zimbra to cse10 for disaster recovery
log "Preparing disaster recovery copy ..."
#check to see if zimbra is running on cse10, if running stop the processes
if ssh -i /root/.ssh/zimbra_trans root@192.168.0.4 'ps aux | grep zimbra | grep -v grep'; then
    log "zimbra is active on cse10, so shutting down"
    #its actuve so shut it down
    ssh -i /root/.ssh/zimbra_trans root@192.168.0.4 '/etc/init.d/zimbra stop'
    sleep 30
    # Kill any orphaned Zimbra processes
    #ssh -i /root/.ssh/zimbra_trans root@192.168.0.4 'kill -9 `ps -u zimbra -o "pid="`'

#else
#    echo "OK"
fi
log "Sending backup files to cse10 ..."
#rsync -avH --delete --force -e "ssh -i /root/.ssh/zimbra_trans" /media/backup/zimbra root@192.168.0.4:/opt/
#rsync -avH --delete --force -e "ssh -i /root/.ssh/zimbra_trans" $TODAYSDIR/zimbra root@192.168.0.4:/opt/
rsync -avH --delete --force -e "ssh -i /root/.ssh/zimbra_trans" $TODAYSDIR/zimbra root@192.168.0.4:/opt/
log "Zimbra transfer complete ..."
rsync -avH --delete --force --exclude svn/ --exclude tmp/ --exclude mysql_backups/ -e "ssh -i /root/.ssh/zimbra_trans" /data/ root@192.168.0.4:/data/
log "Copying complete to cse10 ..."

#backup config files from cs1 and cse10
log "Copying configuration files..."
while read filename
do
#FILENAME=$line
firstchar=${filename:0:1}
#echo $firstchar
	if [ ! $firstchar == "#" ]; then
	    log $filename;
           rsync -aHK $filename $configdir_cs1
           rsync -aHK -e "ssh -i /root/.ssh/zimbra_trans" root@192.168.0.4:$filename $configdir_cse10
	fi
done<$ZBACKUP_SCRIPT/filetransfer.txt
log "Copying configuration files...complete"

# svn dump of site repository
svnadmin dump /data/svn/main_repo > $BACKUP/svn/cosolar.dmp


# rsync directories
rsync -a --delete --exclude svn/ --exclude tmp/ /data/ $BACKUP/data/
rsync -a /root/Desktop/'System Rebuild'/ $BACKUP/'System Rebuild'/
rsync -a $ZBACKUP_SCRIPT/ $BACKUP/scripts/

if [ $DAY == $BACKUPTOUSB ]; then
   #check that USB drive is mounted
#   umount /media/usbdisk
#   mount /dev/sdd1 /media/usbdisk
#   if [ $? -eq 0 ]; then
      log "Starting transfer of files to off-site drive...."
	log "Removing files over 60 days old...."
	find /media/usbdisk -maxdepth 1 -name \*bz2 -ctime +60 -exec rm {} \; -print
#      tar cjf /media/usbdisk/full_cs1.`date +%d-%b-%y`.tar.bz2 /media/backup/

#tar vcjf /media/usbdisk/full_cs1.02-26-12test.tar.bz2 /media/backup/ --exclude /media/backup/mailbox_extract --exclude /media/backup/opt_zimbra.02-25-2012  --exclude /media/backup/opt_zimbra.02-26-2012

      tar cjf /media/usbdisk/full_cs1.`date +%d-%b-%y`.tar.bz2 $BACKUP/ --exclude $BACKUP/mailbox_extract --exclude $YESTERDAYDIR --exclude $TODAYSDIR
#   else
#      log "USB Drive not mounted...transfer of files failed"
#   fi
fi

#at the beginning of each month extract the mailboxes so that they can be manually written to
#DVD's for archive
if [ $DAYNUMBER -lt 2 ]; then
#if [ $DAYNUMBER -eq 15 ]; then
   FQDN=`dnsdomainname`

   #echo $FQDN
   while read name
   do
   #FILENAME=$line
   firstchar=${name:0:1}
   #echo $firstchar
           if [ ! $firstchar == "#" ]; then
#	      log $name@$FQDN
	      #if user mailbox already exists, remove
	      checkdir=$BACKUP/mailbox_extract/$name
	      if [ -d $checkdir ]; then
		 log "Removing Directory $name........"
		 rm -rf $checkdir
	      fi
              #create directory
	      mkdir -p $BACKUP/mailbox_extract/$name
	      #unzip current file
	      unzip $BACKUP/zimbra_files/backup/mailbox/$DAY/$name@$FQDN.zip -d $BACKUP/mailbox_extract/$name
	   fi
   #echo $FILENAME
   done<$ZBACKUP_SCRIPT/mailboxes.txt

#send email reminder -- STILL to DO
#EMAILMESSAGE=/opt/zimbra_backup/scripts/mail.txt
#   SENDMAIL=/opt/zimbra/postfix/sbin/sendmail
#   (
#       echo "To: admin@cosolar.com"
#       echo "Cc: gary@cosolar.com"
#       echo "From: noreply@cosolar.com"
#       echo "Subject: Email Archive"
#       echo "`< $EMAILMESSAGE`"
#    )  |  $SENDMAIL -t
fi
log "Finish time of backup is... `(date +%c)`"
# Calculating time
after="$(date +%s)"
elapsed="$(expr $after - $before)"
hours=$(($elapsed / 3600))
elapsed=$(($elapsed - $hours * 3600))
minutes=$(($elapsed / 60))
seconds=$(($elapsed - $minutes * 60))
log The complete backup lasted : "$hours hours $minutes minutes $seconds seconds"
