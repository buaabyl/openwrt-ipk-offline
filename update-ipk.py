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
import re
import json
import gzip
import hashlib
import requests

#kmod must match kernel version!
#don't mess this version.
openwrt_url_old = 'https://downloads.openwrt.org/chaos_calmer/15.05/'
openwrt_url_new = 'https://downloads.openwrt.org/chaos_calmer/15.05.1/'
openwrt_url     = openwrt_url_old

ar9331_generic  = 'ar71xx/generic/'
ar9331_packages = 'ar71xx/generic/packages/'
packages_gz     = 'Packages.gz'

dirs_list = ['base', 'luci', 'management', 'packages', 'routing', 'telephony']

stdlog = -1

def file_get_gzip(fn):
    f = gzip.open(fn)
    d = f.read()
    f.close()
    return d

def file_put_raw(fn, d):
    f = open(fn, 'wb')
    f.write(d)
    f.close()

def file_get_content(fn):
    f = open(fn)
    d = f.read()
    f.close()
    return d

def file_put_content(fn, d):
    f = open(fn, 'w')
    f.write(d)
    f.close()

def parse_packages_db(fn):
    pattern = re.compile(r'^(\w+): (.+)')

    text = file_get_gzip(fn)

    result = []
    for info_block in text.split('\n\n'):
        lines = info_block.split('\n')
        l = []

        #combine multiline descriptions.
        for line in lines:
            if line.startswith(' '):
                l[-1] = l[-1] + '\\n' + line
            else:
                l.append(line)

        #parse information
        m = {}
        for line in l:
            res = pattern.search(line)
            if res:
                m[res.groups()[0]] = res.groups()[1]

        if len(m) > 0:
            result.append(m)

    #jstr = json.dumps(result, indent=4, sort_keys=True)
    #file_put_content('parsed.json', jstr)
    return result

def urljoin(url1, url2):
    if not url1.endswith('/'):
        url1 = url1 + '/'
    if url2.startswith('/'):
        url2 = url2[1:]
    return url1 + url2

def download_package(url, fn):
    msg = 'GET: %s' % url
    print(msg)
    stdlog.write(msg + '\n')

    r = requests.get(url)
    if r.status_code == 200:
        msg = '     status=%d, content-type="%s", content-length=%s' % \
                (r.status_code, r.headers['content-type'], r.headers['content-length'])
    else:
        msg = '     status=%d' % r.status_code
    file_put_raw(fn, r.content)

    print(msg)
    stdlog.write(msg + '\n')

    return r.status_code

def md5sum(fn):
    f = open(fn, 'rb')
    d = f.read()
    f.close()
    digest = hashlib.md5(d)
    return digest.hexdigest()

if __name__ == '__main__':
    stdlog = open('update-ipk.log','w')

    baseurl = urljoin(openwrt_url, ar9331_packages)
    print(baseurl)

    for dirname in dirs_list:
        print('>DIR', dirname)

        if not os.path.isdir(dirname):
            os.mkdir(dirname)

        filename= urljoin(dirname, 'Packages.gz')
        url     = urljoin(baseurl, filename)
        ret = download_package(url, filename)
        if ret != 200:
            break
        packages_db = parse_packages_db(filename)

        package_id  = 1
        nr_packages = len(packages_db)
        for package in packages_db:
            print('(%d/%d)' % (package_id, nr_packages))
            package_id = package_id + 1

            expect  = package['MD5Sum']
            filename= urljoin(dirname, package['Filename'])
            url     = urljoin(baseurl, filename)
            if os.path.isfile(filename):
                current = md5sum(filename)
                if expect == current:
                    print('IGN:', url)
                    continue

            ret = download_package(url, filename)
            if ret != 200:
                break

            current = md5sum(filename)
            if expect != current:
                print('     Expect MD5Sum:', expect)
                print('     Actual MD5Sum:', current)

        if ret != 200:
            break

    stdlog.close()

