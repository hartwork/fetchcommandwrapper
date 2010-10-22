#!/usr/bin/env python
# Copyright (C) 2010 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GPL v3 or later

MAX_STREAMS = 5
LINK_SPEED_BYTES = 600 * 1024


import sys

# Greeting
VERSION = (0, 2)
print 'fetchcommandwrapper', '.'.join(str(e) for e in VERSION)
print


# Command line argument parsing
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

import os

if not os.path.exists('/usr/bin/aria2c'):
    print >>sys.stderr, 'ERROR: net-misc/aria2 not installed'
    sys.exit(1)

if not os.path.isdir(distdir):
    print >>sys.stderr, 'ERROR: Path "%s" not a directory' % distdir
    sys.exit(1)

if continue_flag:
    file_fullpath = os.path.join(distdir, file_basename)
    if not os.path.isfile(file_fullpath):
        print >>sys.stderr, 'ERROR: Path "%s" not an existing file' % file_fullpath
        sys.exit(1)

print 'URI = ' + uri
print 'DISTDIR = ' + distdir
print 'FILE = ' + file_basename
print


# Collect mirror URIs
import subprocess

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

print 'Involved mirrors:'
print '\n'.join('  - ' + e for e in supported_mirror_uris)
print '  (%d mirrors)' % len(supported_mirror_uris)
print

if len(supported_mirror_uris) < MAX_STREAMS:
    print >>sys.stderr, 'WARNING:  Please specify at least %d URIs in GENTOO_MIRRORS.' % MAX_STREAMS
    print >>sys.stderr, '          The more the better, order from fast/near to slow/far.' 
    print >>sys.stderr


# Make list of URIs
final_uris = [uri, ]
for i, mirror_uri in enumerate(supported_mirror_uris):
    if uri.startswith(mirror_uri):
        local_part = uri[len(mirror_uri):]
        final_uris = [e + local_part for e in supported_mirror_uris[i:]]
        break


# Compose call arguments
wanted_connections = min(MAX_STREAMS, len(final_uris))
wanted_minimum_link_speed = LINK_SPEED_BYTES / wanted_connections / 3
if len(final_uris) > MAX_STREAMS:
    drop_slow_links = True
else:
    drop_slow_links = False

print 'Targetting %d connections, additional %d for backup' \
    % (wanted_connections, max(0, len(final_uris) - MAX_STREAMS))
print

args = ['/usr/bin/aria2c', '-d', distdir, '-o', file_basename]
if drop_slow_links:
    args.append('--lowest-speed-limit=%s' % wanted_minimum_link_speed)
if continue_flag:
    args.append('--continue')
args.append('--max-tries=2')
args.append('--split=%d' % wanted_connections)
args.append('--max-connection-per-server=1')
args.append('--uri-selector=inorder')
args.extend(final_uris)


# Invoke aria2
print 'Running... #', ' '.join(args)
p = subprocess.Popen(args)
(out, err) = p.communicate()
