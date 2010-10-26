#!/usr/bin/env python
# Copyright (C) 2010 Sebastian Pipping <sebastian@pipping.org>
# Copyright (C) 2010 Andrew Karpow <andy@mailbox.tu-berlin.de>
# Licensed under GPL v3 or later

MAX_STREAMS = 5
LINK_SPEED_BYTES = 600 * 1024


import sys


def print_greeting():
    from fetchcommandwrapper.version import VERSION_STR
    print 'fetchcommandwrapper', VERSION_STR
    print


def parse_parameters():
    if len(sys.argv) != 5:
        print >>sys.stderr, 'USAGE: %s --continue|--fresh URI DISTDIR FILE' % sys.argv[0]
        sys.exit(1)

    if sys.argv[1] == '--continue':
        continue_flag = True
    elif sys.argv[1] == '--fresh':
        continue_flag = False
    else:
        print >>sys.stderr, 'USAGE: %s --continue|--fresh URI DISTDIR FILE' % sys.argv[0]
        sys.exit(1)

    uri=sys.argv[2]
    distdir=sys.argv[3].rstrip('/')
    file_basename=sys.argv[4]
    return uri, distdir, file_basename, continue_flag

uri, distdir, file_basename, continue_flag = parse_parameters()

import os
import subprocess

file_fullpath = os.path.join(distdir, file_basename)

def invoke_wget(file_fullpath, continue_flag, uri):
    args = ['/usr/bin/wget', '-O', file_fullpath]
    args.append('--tries=5')
    args.append('--timeout=60')
    args.append('--passive-ftp')
    if continue_flag:
        args.append('--continue')
    args.append(uri)

    # Invoke wget
    print 'Running... #', ' '.join(args)
    ret = subprocess.call(args)
    sys.exit(ret)

if not os.path.exists('/usr/bin/aria2c'):
    print >>sys.stderr, 'ERROR: net-misc/aria2 not installed, falling back to net-misc/wget'
    invoke_wget(file_fullpath, continue_flag, uri)

if not os.path.isdir(distdir):
    print >>sys.stderr, 'ERROR: Path "%s" not a directory' % distdir
    sys.exit(1)

if continue_flag:
    if not os.path.isfile(file_fullpath):
        print >>sys.stderr, 'ERROR: Path "%s" not an existing file' % file_fullpath
        sys.exit(1)


def print_invocation_details():
    print 'URI = ' + uri
    print 'DISTDIR = ' + distdir
    print 'FILE = ' + file_basename
    print


# Collect mirror URIs

def gentoo_mirrors():
    p = subprocess.Popen(['/bin/bash', '-c', 'source /etc/make.conf; echo ${GENTOO_MIRRORS}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    if err:
        print >>sys.stderr, 'ERROR', err
        sys.exit(1)
    return out.rstrip('\n').split(' ')
    
mirror_uris = gentoo_mirrors()

def supported(uri):
    return uri.startswith('http://') \
        or uri.startswith('https://') \
        or uri.startswith('ftp://')

supported_mirror_uris = [e for e in mirror_uris if supported(e)]


def print_mirror_details():
    print 'Involved mirrors:'
    print '\n'.join('  - ' + e for e in supported_mirror_uris)
    print '  (%d mirrors)' % len(supported_mirror_uris)
    print

    if len(supported_mirror_uris) < MAX_STREAMS:
        print >>sys.stderr, 'WARNING:  Please specify at least %d URIs in GENTOO_MIRRORS.' % MAX_STREAMS
        print >>sys.stderr, '          The more the better.'
        print >>sys.stderr


def make_final_uris(uri, supported_mirror_uris):
    final_uris = [uri, ]
    mirrors_involved = False
    for i, mirror_uri in enumerate(supported_mirror_uris):
        if uri.startswith(mirror_uri):
            if i != 0:
                # Portage calls us for each mirror URI. Therefore we need to error out
                # on all but the first one, so we try each mirrror once, at most.
                # This happens, when a file is not mirrored, e.g. with sunrise ebuilds.
                print >>sys.stderr, 'ERROR: All Gentoo mirrors tried already, exiting.'
                sys.exit(1)

            mirrors_involved = True

            local_part = uri[len(mirror_uri):]
            final_uris = [e + local_part for e in supported_mirror_uris]
            import random
            random.shuffle(final_uris)
            break
    return final_uris, mirrors_involved

final_uris, mirrors_involved = make_final_uris(uri, supported_mirror_uris)

print_greeting()
print_invocation_details()

if mirrors_involved:
    print_mirror_details()


def invoke_aria2(distdir, file_basename, continue_flag,  final_uris):
    # Compose call arguments
    wanted_connections = min(MAX_STREAMS, len(final_uris))
    wanted_minimum_link_speed = LINK_SPEED_BYTES / wanted_connections / 3
    if len(final_uris) > MAX_STREAMS:
        drop_slow_links = True
    else:
        drop_slow_links = False

    if len(final_uris) > 1:
        print 'Targetting %d random connections, additional %d for backup' \
            % (wanted_connections, max(0, len(final_uris) - MAX_STREAMS))
        print

    args = ['/usr/bin/aria2c', '-d', distdir, '-o', file_basename]
    if drop_slow_links:
        args.append('--lowest-speed-limit=%s' % wanted_minimum_link_speed)
    if continue_flag:
        args.append('--continue')
    args.append('--max-tries=2')
    args.append('--check-certificate=false')
    args.append('--user-agent=Wget/1.12')
    args.append('--split=%d' % wanted_connections)
    args.append('--max-connection-per-server=1')
    args.append('--uri-selector=inorder')
    args.extend(final_uris)

    # Invoke aria2
    print 'Running... #', ' '.join(args)
    p = subprocess.Popen(args)
    (out, err) = p.communicate()

invoke_aria2(distdir, file_basename, continue_flag, final_uris)
