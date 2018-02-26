Re-send captured emails using SMTP
==================================

This tool, 'mailreplay', is intended to help in testing email pipelines by
reading captured emails from files, figuring out the sender and recipient, and
re-injecting them to localhost:25 using SMTP. (If the captured emails have a
final recipient on a different system than localhost, you need to make sure
that the MTA is blocked from sending the emails out into the world during
testing.)

An initial envelope From line is used as the sender, if available. Otherwise,
the email header From: field is used. The email header Received: fields are
used to figure out the envelope recipient.

Many other tools exist that will read an an email from file and send it using
SMTP, but they all seem to have in common that they need to be given the
recipient address on the command line, and by default will use the logged-in
user as the sender address. For email pipline testing purposes, when a varied
set of senders and recipients are desired, this doesn't scale easily, hence
this tool.
