#!/bin/python
# -*- coding:utf-8 -*-
#  
#  Copyright 2013 buaa.byl@gmail.com
#
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#
from __future__ import print_function
import sys
import os
import imp
import json
import glob

stdlog = -1

if __name__ == '__main__':
    stdlog = open('check-ipk.log','w')

    module = imp.load_source('update_ipk_py', 'update-ipk.py')
    packages_gz         = module.packages_gz
    dirs_list           = module.dirs_list
    file_get_gzip       = module.file_get_gzip
    file_put_content    = module.file_put_content
    parse_packages_db   = module.parse_packages_db
    md5sum              = module.md5sum


    allfiles = {}
    for dirname in dirs_list:
        l = glob.glob(os.path.join(dirname, '*.*'))
        for fn in l:
            if fn.endswith('\\Packages.gz'):
                continue
            if fn.endswith('\\Packages.sig'):
                continue
            allfiles[fn] = True

    file_put_content('all-files.lst', '\n'.join(allfiles))

    errorfiles = []
    lostfiles = []

    for dirname in dirs_list:
        print('>DIR', dirname)

        if not os.path.isdir(dirname):
            os.mkdir(dirname)

        filename= os.path.join(dirname, 'Packages.gz')
        packages_db = parse_packages_db(filename)

        for package in packages_db:
            expect  = package['MD5Sum']
            filename= os.path.join(dirname, package['Filename'])
            if not os.path.isfile(filename):
                print('LOST:', filename)
                stdlog.write('LOST: %s\n' % filename)
                lostfiles.append(filename)
                continue

            current = md5sum(filename)
            if expect == current:
                print('OK:', filename)
                stdlog.write('OK: %s\n' % filename)
                if filename in allfiles:
                    del allfiles[filename]
            else:
                print('ERR:', filename)
                stdlog.write('ERR: %s\n' % filename)
                errorfiles.append(filename)


    file_put_content('orphan-files.lst', '\n'.join(allfiles))

    l = []
    if len(allfiles) > 0:
        for fn in allfiles:
            l.append('rm "%s"' % fn)
        print('Orphan files: %d' % len(l))
        file_put_content('rm-orphanfiles.cmd', '\n'.join(l))

    if len(errorfiles) > 0:
        print('Error files: %d' % len(errorfiles))
        file_put_content('errorfiles.lst', '\n'.join(errorfiles))

    if len(lostfiles) > 0:
        print('Lost files: %d' % len(lostfiles))
        file_put_content('lost-files.lst', '\n'.join(lostfiles))

    stdlog.close()

