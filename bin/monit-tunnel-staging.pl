#!/usr/bin/perl

# Modified copy of couchdb-tunntel.pl, adopted for monit.
# Usage: monit-tunnel.pl [start|stop]
# Access the Monit dashboard by way of an SSH tunnel.
#
# Original copyright header:
#   Copyright (c) 2010 Linode, LLC
#   Author: Philip C. Paradis <pparadis@linode.com>
#   Modifications: Sam Kleinman <sam@linode.com>

$sshd_port   = "941";
$remote_user = $ENV{'USER'};
$remote_host = "msg";
$remote_port = "2812";
$remote_ip   = "127.0.0.1";
$local_ip    = "127.0.0.1";
$local_port  = "2812";

$a = shift;
$a =~ s/^\s+//;
$a =~ s/\s+$//;

$pid=`ps ax|grep ssh|grep $local_port|grep $remote_port`;
$pid =~ s/^\s+//;
@pids = split(/\n/,$pid);
foreach $pid (@pids)
{
 if ($pid =~ /ps ax/) { next; }
 split(/ /,$pid);
}

if (lc($a) eq "start")
{
 if ($_[0]) { print "Monit tunnel already running.\n"; exit 1; }
 else
 {
  system "ssh -p $sshd_port -f -L $local_ip:$local_port:$remote_ip:$remote_port $remote_user\@$remote_host -N";
  exit 0;
 }
}
elsif (lc($a) eq "stop")
{
 if ($_[0]) { kill 9,$_[0]; exit 0; }
 else { exit 1; }
}
else
{
 print "Usage: monit-tunnel.pl [start|stop]\n";
 exit 1;
}

