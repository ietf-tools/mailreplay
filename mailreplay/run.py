#!/bin/env python
# -*- coding: utf-8 -*-
# Copyright The IETF Trust 2017, All Rights Reserved

"""
NAME
  mailreplay - Re-send captured emails using SMTP

...

DESCRIPTION
  mailreplay is intended to help in testing email pipelines by reading
  captured emails from files, figuring out the sender and recipient, and
  re-injecting them to localhost:25 using SMTP. (If the captured emails have
  a final recipient on a different system than localhost, you need to make
  sure that the MTA is blocked from sending the emails out into the world
  during testing.)

  An initial envelope From line is used as the sender, if available. Otherwise,
  the email header From: field is used. The email header Received: fields are
  used to figure out the envelope recipient.

  Many other tools exist that will read an an email from file and send it using
  SMTP, but they all seem to have in common that they need to be given the
  recipient address on the command line, and by default will use the logged-in
  user as the sender address. For email pipline testing purposes, when a varied
  set of senders and recipients are desired, this doesn't scale easily, hence
  this tool.


OPTIONS
...

AUTHOR
  Written by Henrik Levkowetz, <henrik@levkowetz.com>

COPYRIGHT
  Copyright (c) 2017, The IETF Trust.
  All rights reserved.

  Licenced under the 3-clause BSD license; see the file LICENSE
  for details.
"""


from __future__ import print_function, unicode_literals, division


from mailreplay.__init__ import __version__
from mailreplay.replay import send_mail_from_file

try:
    import debug
    debug.debug = True
except ImportError:
    pass

try:
    from pprint import pformat
except ImportError:
    pformat = lambda x: x

_prolog, _middle, _epilog = __doc__.split('...')

# ----------------------------------------------------------------------
#
# This is the entrypoint which is invoked from command-line scripts:

class Options(object):
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            if not k.startswith('__'):
                setattr(self, k, v)
    pass

def run():
    import sys, os, argparse, smtplib, rfc822
    from pathlib2 import Path
    global _prolog, _middle, _epilog

    program = os.path.basename(sys.argv[0])
    #progdir = os.path.dirname(sys.argv[0])

    # ----------------------------------------------------------------------
    # Parse config file
    # default values
    conf = {
        'mailhost':         'localhost',
        'replacement':      [
            ],
        }
    for p in ['.', os.environ.get('HOME','.'), '/etc/', ]:
        rcpath = Path(p)
        if rcpath.exists():
            rcfn = rcpath / '.mailreplayrc'
            if rcfn.exists():
                execfile(str(rcfn), conf)
                break
    options = Options(**conf)

    # ----------------------------------------------------------------------
    def say(s):
        msg = "%s\n" % (s)
        sys.stderr.write(msg)

    # ----------------------------------------------------------------------
    def note(s):
        msg = "%s\n" % (s)
        if not options.quiet:
            sys.stderr.write(msg)

    # ----------------------------------------------------------------------
    def die(s, error=1):
        msg = "\n%s: Error:  %s\n\n" % (program, s)
        sys.stderr.write(msg)
        sys.exit(error)

    # ----------------------------------------------------------------------
    # Parse options

    def commalist(value):
        return [ s.strip() for s in value.split(',') ]

    class HelpFormatter(argparse.RawDescriptionHelpFormatter):
        def _format_usage(self, usage, actions, groups, prefix):
            global _prolog
            if prefix is None or prefix == 'usage: ':
                prefix = 'SYNOPSIS\n  '
            return _prolog+super(HelpFormatter, self)._format_usage(usage, actions, groups, prefix)

    parser = argparse.ArgumentParser(description=_middle, epilog=_epilog,
                                     formatter_class=HelpFormatter, add_help=False)

    group = parser.add_argument_group(argparse.SUPPRESS)

    group.add_argument('EMAIL', nargs='*',                              help="Files with captured emails to be replayed")
    group.add_argument('-d', '--debug', action='store_true',            help="turn on debugging")
    group.add_argument('-D', '--date', default=None,                    help="Use the given date string instead of the original")
    group.add_argument('-h', '--help', action='help',                   help="show this help message and exit")
    group.add_argument('-H', '--helo', default=None,                    help="The HELO (or EHLO) name to use")
    group.add_argument('-p', '--port', type=int, default=25,            help="Use the given SMTP port instead of 25")
    group.add_argument('-r', '--replacement', action='append',          help="domain replacement <old>,<new>, as in '@example.com,@example.org' to apply to recipient")
    group.add_argument('-v', '--version', action='store_true',          help="output version information, then exit")
    group.add_argument('-V', '--verbose', action='store_true',          help="be (slightly) more verbose")

    options = parser.parse_args(namespace=options)

    if options.debug:
        debug.pprint('options.__dict__')

    # ----------------------------------------------------------------------
    # The program itself    

    if hasattr(globals(), 'debug'):
        debug.debug = options.debug

    if options.version:
        print(program, __version__)
        sys.exit(0)

    if options.date:
        if not rfc822.parsedate_tz(options.date):
            die("The date string '%s' is not a recognized email date.\n"
                "   Expected something like 'Mon, 20 Nov 1995 19:12:08 -0500'.\n"
                "   On some systems, the command 'date -R' will give the current date and time\n"
                "   in the right format." % (options.date, ))

    kwargs = {}
    if hasattr(options, 'helo') and options.helo:
        kwargs['local_hostname'] = options.helo
    server = smtplib.SMTP('localhost', options.port, **kwargs)
    server.set_debuglevel(1 if options.debug else 0)

    for file in options.EMAIL:
        try:
            if options.debug:
                debug.show('file')
            send_mail_from_file(server, file, options)
        except Exception as e:
            sys.stderr.write("Failure processing %s: %s\n" % (file, e))
            raise


if __name__ == '__main__':
    run()
    
