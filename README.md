# openwrt-ipk-offline
Download openwrt ipk packages

```python
openwrt_url     = 'https://downloads.openwrt.org/chaos_calmer/15.05/'
ar9331_packages = 'ar71xx/generic/packages/'
```

update-ipk.py: get Packages and then check local repos, download if not exist or MD5Sum mismatch.
```
GET: https://downloads.openwrt.org/chaos_calmer/15.05/ar71xx/generic/packages/base/Packages.gz
     status=200, content-type="application/octet-stream", content-length=121975
GET: https://downloads.openwrt.org/chaos_calmer/15.05/ar71xx/generic/packages/luci/Packages.gz
     status=200, content-type="application/octet-stream", content-length=90639
......
```

check-ipk.py: check local repos, generate rm-orphanfiles.cmd to delete duplicated files.



