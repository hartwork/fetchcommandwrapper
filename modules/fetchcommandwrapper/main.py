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
    USAGE = "\n  %prog [OPTIONS] URI DISTDIR FILE"""

    from optparse import OptionParser
    from fetchcommandwrapper.version import VERSION_STR
    parser = OptionParser(usage=USAGE, version=VERSION_STR)

    parser.add_option("-c", "--continue",
        action="store_true", dest="continue_flag", default=False,
        help="continue previous download")
    parser.add_option("--fresh",
        action="store_false", dest="continue_flag", default=False,
        help="do not continue previous download (default)")

    (opts, args) = parser.parse_args()
    if len(args) != 3:
        parser.print_usage()
        sys.exit(1)

    uri, distdir, file_basename = args
    distdir = distdir.rstrip('/')

    return uri, distdir, file_basename, opts.continue_flag


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
    import subprocess
    return subprocess.call(args)


def print_invocation_details(uri, distdir, file_basename):
    print 'URI = ' + uri
    print 'DISTDIR = ' + distdir
    print 'FILE = ' + file_basename
    print


def gentoo_mirrors():
    import subprocess
    p = subprocess.Popen(['/bin/bash', '-c', 'source /etc/make.conf; echo ${GENTOO_MIRRORS}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    if err:
        print >>sys.stderr, 'ERROR', err
        sys.exit(1)
    return out.rstrip('\n').split(' ')


def supported(uri):
    return uri.startswith('http://') \
        or uri.startswith('https://') \
        or uri.startswith('ftp://')


def print_mirror_details(supported_mirror_uris):
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
    import subprocess
    return subprocess.call(args)


def main():
    uri, distdir, file_basename, continue_flag = parse_parameters()

    import os

    file_fullpath = os.path.join(distdir, file_basename)

    if not os.path.exists('/usr/bin/aria2c'):
        print >>sys.stderr, 'ERROR: net-misc/aria2 not installed, falling back to net-misc/wget'
        ret = invoke_wget(file_fullpath, continue_flag, uri)
        sys.exit(ret)

    if not os.path.isdir(distdir):
        print >>sys.stderr, 'ERROR: Path "%s" not a directory' % distdir
        sys.exit(1)

    if continue_flag:
        if not os.path.isfile(file_fullpath):
            print >>sys.stderr, 'ERROR: Path "%s" not an existing file' % file_fullpath
            sys.exit(1)

    supported_mirror_uris = [e for e in gentoo_mirrors() if supported(e)]

    final_uris, mirrors_involved = make_final_uris(uri, supported_mirror_uris)

    print_greeting()
    print_invocation_details(uri, distdir, file_basename)

    if mirrors_involved:
        print_mirror_details(supported_mirror_uris)

    ret = invoke_aria2(distdir, file_basename, continue_flag, final_uris)
    sys.exit(ret)


if __name__ == '__main__':
    main()
