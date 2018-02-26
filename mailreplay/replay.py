#!/bin/env python
# -*- coding: utf-8 -*-
# Copyright The IETF Trust 2017, All Rights Reserved

from __future__ import print_function, unicode_literals, division

import re
import sys
import email
import smtplib
import socket
import datetime
import dateutil.tz

# from email.utils import make_msgid, formatdate, formataddr as simple_formataddr, parseaddr, getaddresses
# from email.mime.text import MIMEText
# from email.mime.message import MIMEMessage
# from email.mime.multipart import MIMEMultipart
# from email.header import Header
# from email import message_from_file
# from email import charset as Charset

import debug


address_list = []

def send_mail_from_file(server, file, options):
    global address_list
    #
    with open(file) as f:
        m = email.message_from_file(f)
    # get sender
    from_field = m.get_unixfrom()
    if from_field:
        from_field = from_field.split()[1]
    else:
        for name in ['Return-Path', 'From', ]:
            if m.get(name):
                from_field = m[name]
                break
    if not from_field:
        sys.stderr.write("Could not find a sender in %s, skipping it\n" % file)
        return
    sender = email.utils.parseaddr(from_field)[1]
    # get recipient
    info = {}
    for received in m.get_all('Received'):
        if not ';' in received:
            continue
        datestring = received.split(';', 1)[1]
        datetuple = email.utils.parsedate_tz(datestring)
        if datetuple and datetuple[9]:
            date = datetime.datetime(*datetuple[:6], tzinfo=dateutil.tz.tzoffset(None, datetuple[9]) )
            info[date] = {}
            for kw in ['from', 'by', 'with', 'for', 'via', 'id']:
                match = re.search(r'(?<=%s )(\S+ (\([^)]+\))?)'%kw, received)
                if match:
                    info[date][kw] = match.group(0)
    dates = info.keys()
    dates.sort()
    recipient = None
    for d in dates:
        if 'for' in info[d]:
            recipient = info[d]['for'].strip('<>; ')
            break
    if not recipient:
        for name in ['X-Original-To', 'Delivered-To']:
            if m.get(name):
                recipient = m[name]
                break
    if not recipient:
        sys.stderr.write("Could not find a recipient in %s, skipping it\n" % file)
        return
    for replacement in options.replacement:
        old, new = replacement.split(':', 1)
        if '@' in old and '@' in new:
            recipient = recipient.replace(old, new)

    if options.debug:
        debug.say('Replaying %s ==> %s'%(sender,recipient))
    server.verify(recipient)
    unhandled = {}
    try:
        unhandled.update( server.sendmail(sender, recipient, m.as_string()) )
    except smtplib.SMTPRecipientsRefused as e:
        unhandled.update( e.recipients )
    if unhandled != {}:
        print(str(unhandled))
        for recv in unhandled:
            reason = unhandled[recv]    
            sys.stderr.write("Failure sending email from file %s: %s ==> %s: %s" % (file, sender, recv, reason))
        raise RuntimeError("Mail replay failure")
