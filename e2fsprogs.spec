%define	_root_sbindir	/sbin
%define	_root_libdir	/%{_lib}

Summary: Utilities for managing the second extended (ext2) filesystem.
Name: e2fsprogs
Version: 1.23
Release: 1
Copyright: GPL
Group: System Environment/Base
Source:  ftp://download.sourceforge.net/pub/sourceforge/e2fsprogs/e2fsprogs-%{version}.tar.gz
Patch1: e2fsprogs-1.19-mountlabel3.patch
Url: http://e2fsprogs.sourceforge.net/
Prereq: /sbin/ldconfig
BuildRoot: %{_tmppath}/%{name}-root

%description
The e2fsprogs package contains a number of utilities for creating,
checking, modifying, and correcting any inconsistencies in second
extended (ext2) filesystems. E2fsprogs contains e2fsck (used to
repair filesystem inconsistencies after an unclean shutdown), mke2fs
(used to initialize a partition to contain an empty ext2 filesystem),
debugfs (used to examine the internal structure of a filesystem, to
manually repair a corrupted filesystem, or to create test cases for
e2fsck), tune2fs (used to modify filesystem parameters), and most of
the other core ext2fs filesystem utilities.

You should install the e2fsprogs package if you need to manage the
performance of an ext2 filesystem.

%package devel
Summary: Ext2 filesystem-specific static libraries and headers.
Group: Development/Libraries
Requires: e2fsprogs = %{version}
Prereq: /sbin/install-info

%description devel
E2fsprogs-devel contains the libraries and header files needed to
develop second extended (ext2) filesystem-specific programs.

You should install e2fsprogs-devel if you want to develop ext2
filesystem-specific programs. If you install e2fsprogs-devel, you'll
also want to install e2fsprogs.

%prep
%setup -q
%patch1 -p1 -b .mountlabel3

chmod 755 configure
autoconf

%build
%configure --enable-elf-shlibs
make libs progs docs

%install
rm -rf $RPM_BUILD_ROOT
export PATH=/sbin:$PATH

make install install-libs DESTDIR="$RPM_BUILD_ROOT" \
	root_sbindir=%{_root_sbindir} root_libdir=%{_root_libdir}

{ cd ${RPM_BUILD_ROOT}%{_libdir}
  ln -sf %{_root_libdir}/libcom_err.so.2 libcom_err.so
  ln -sf %{_root_libdir}/libe2p.so.2 libe2p.so
  ln -sf %{_root_libdir}/libext2fs.so.2 libext2fs.so
  ln -sf %{_root_libdir}/libss.so.2 libss.so
  ln -sf %{_root_libdir}/libuuid.so.1 libuuid.so
}

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post devel
if [ -x /sbin/install-info ]; then
    /sbin/install-info %{_infodir}/libext2fs.info.gz %{_infodir}/dir
fi
exit 0

%postun devel
if [ $1 = 0 ]; then
   /sbin/install-info --delete %{_infodir}/libext2fs.info.gz %{_infodir}/dir
fi
exit 0

%files
%defattr(-,root,root)
%doc README RELEASE-NOTES

%{_root_sbindir}/badblocks
%{_root_sbindir}/debugfs
%{_root_sbindir}/dumpe2fs
%{_root_sbindir}/e2fsck
%{_root_sbindir}/e2label
%{_root_sbindir}/fsck
%{_root_sbindir}/fsck.ext2
%{_root_sbindir}/fsck.ext3
%{_root_sbindir}/mke2fs
%{_root_sbindir}/mkfs.ext2
%{_root_sbindir}/resize2fs
%{_root_sbindir}/tune2fs
%{_sbindir}/mklost+found

%{_root_libdir}/libcom_err.so.*
%{_root_libdir}/libe2p.so.*
%{_root_libdir}/libext2fs.so.*
%{_root_libdir}/libss.so.*
%{_root_libdir}/libuuid.so.*

%{_bindir}/chattr
%{_bindir}/lsattr
%{_bindir}/uuidgen
%{_mandir}/man1/chattr.1*
%{_mandir}/man1/lsattr.1*
%{_mandir}/man1/uuidgen.1*

%{_mandir}/man3/libuuid.3*
%{_mandir}/man3/uuid_clear.3*
%{_mandir}/man3/uuid_compare.3*
%{_mandir}/man3/uuid_copy.3*
%{_mandir}/man3/uuid_generate.3*
%{_mandir}/man3/uuid_is_null.3*
%{_mandir}/man3/uuid_parse.3*
%{_mandir}/man3/uuid_time.3*
%{_mandir}/man3/uuid_unparse.3*

%{_mandir}/man8/badblocks.8*
%{_mandir}/man8/debugfs.8*
%{_mandir}/man8/dumpe2fs.8*
%{_mandir}/man8/e2fsck.8*
%{_mandir}/man8/e2label.8*
%{_mandir}/man8/fsck.8*
%{_mandir}/man8/mke2fs.8*
%{_mandir}/man8/mklost+found.8*
%{_mandir}/man8/resize2fs.8*
%{_mandir}/man8/tune2fs.8*

%files devel
%defattr(-,root,root)
%{_infodir}/libext2fs.info*
%{_bindir}/compile_et
%{_bindir}/mk_cmds

%{_libdir}/libcom_err.a
%{_libdir}/libcom_err.so
%{_libdir}/libe2p.a
%{_libdir}/libe2p.so
%{_libdir}/libext2fs.a
%{_libdir}/libext2fs.so
%{_libdir}/libss.a
%{_libdir}/libss.so
%{_libdir}/libuuid.a
%{_libdir}/libuuid.so

%{_datadir}/et
%{_datadir}/ss
%{_includedir}/et
%{_includedir}/ext2fs
%{_includedir}/ss
%{_includedir}/uuid
%{_mandir}/man1/compile_et.1*
%{_mandir}/man3/com_err.3*

%changelog
* Sun Aug 26 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.23. This was requested to support the "auto" fstype
  to ease ext2 <-> ext3 conversions.

* Tue Jul 24 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- add some more man-pages, patch by <Martin.Wilck@fujitsu-siemens.com>

* Tue Jun 26 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- make sure "configure" is writable

* Mon Jun 25 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.22

* Tue Jun 19 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.21

* Mon Jun 11 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- add endian patch from sct@redhat.com  #44104

* Tue May 29 2001 Than Ngo <than@redhat.com>
- update to 1.20
- add Url

* Tue May 15 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- make sure ldconfig doesn't have any input and scripts end
  with "exit 0"

* Tue May 15 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- update to e2fsprogs-1.20-WIP-0514.tar.gz

* Sun Apr 15 2001 Alan Eldridge <alane@geeksrus.net>
- Added 16K buffer for reading /proc/partitions in 
  get_label_by_device.c to correct problems with LABEL= in fsck 
  caused by not reading /proc/partitions in a single read() call;
  if somebody has a "partitions" > 16K, it may still fail ...
* Fri Apr 06 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- add further IDE and SCSI disks to a hardcoded list in fsck #34190

* Tue Feb 27 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- require the main rpm from the devel rpm

* Thu Feb 22 2001 Helge Deller <hdeller@redhat.de>
- fix fsck -A bug (#21242)

* Mon Feb 12 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- fix bug with 16 byte long labels #27071

* Mon Sep 11 2000 Jeff Johnson <jbj@redhat.com>
- build for Red Hat 7.1.

* Tue Aug  8 2000 Jeff Johnson <jbj@redhat.com>
- merge LABEL patch.
- update to 1.19.

* Tue Jul 25 2000 Erik Troan <ewt@redhat.com>
- fixed LABEL handling

* Wed Jul 19 2000 Jakub Jelinek <jakub@redhat.com>
- rebuild to cope with glibc locale binary incompatibility

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Mon Jun 26 2000 Matt Wilson <msw@redhat.com>
- added resize2fs from the WIP snapshot

* Thu Jun 15 2000 Matt Wilson <msw@redhat.com>
- patched to build against linux 2.4 headers

* Mon Jun  5 2000 Jeff Johnson <jbj@redhat.com>
- FHS packaging.

* Fri Apr 28 2000 Bill Nottingham <notting@redhat.com>
- fix for ia64

* Sat Feb  5 2000 Bill Nottingham <notting@redhat.com>
- add install-info scripts

* Thu Feb 03 2000 Elliot Lee <sopwith@redhat.com>
- Fix bug #8585 (Y2K problems in debugfs)

* Wed Feb 02 2000 Jakub Jelinek <jakub@redhat.com>
- allow multiline errors in et, so that other programs
  can use compile_et (from Kerberos)

* Thu Jan 13 2000 Jeff Johnson <jbj@redhat.com>
- build 1.18 for 6.2.

* Tue Oct 26 1999 Bill Nottingham <notting@redhat.com>
- update to 1.17

* Mon Oct 25 1999 Bill Nottingham <notting@redhat.com>
- update to 1.16

* Thu Oct 21 1999 Bill Nottingham <notting@redhat.com>
- add patch to fix SIGUSR1 kills.

* Mon Oct 04 1999 Cristian Gafton <gafton@redhat.com>
- rebuild against new glibc in the sparc tree

* Thu Sep 23 1999 Jakub Jelinek <jakub@redhat.com>
- update mke2fs man page so that it reflects changes in mke2fs
  netweem 1.14 and 1.15

* Thu Aug  5 1999 Bill Nottingham <notting@redhat.com>
- fix lsattr on alpha

* Thu Jul 29 1999 Jeff Johnson <jbj@redhat.com>
- update to 1.15.

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 4)

* Tue Mar 16 1999 Cristian Gafton <gafton@redhat.com>
- fix fsck segfault

* Tue Feb  2 1999 Jeff Johnson <jbj@redhat.com>
- update to 1.14
- use %configure to generate config.sub on arm

* Thu Jan 14 1999 Jeff Johnson <jbj@redhat.com>
- fix /usr/bin/compile_et and doco for com_err.h (#673)

* Thu Jan 07 1999 Cristian Gafton <gafton@redhat.com>
- build with prefix=/usr
- add arm patch

* Mon Dec 28 1998 Jeff Johnson  <jbj@redhat.com>
- update to 1.13.

* Fri Aug 28 1998 Jeff Johnson <jbj@redhat.com>
- recompile statically linked binary for 5.2/sparc

* Mon Jul 13 1998 Jeff Johnson <jbj@redhat.com>
- upgrade to 1.12.

* Thu May 07 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Thu Apr 30 1998 Cristian Gafton <gafton@redhat.com>
- include <asm/types.h> to match kernel types in utils

* Tue Oct 14 1997 Donnie Barnes <djb@redhat.com>
- spec file cleanups

* Wed Oct 01 1997 Erik Troan <ewt@redhat.com>
- fixed broken llseek() prototype 

* Wed Aug 20 1997 Erik Troan <ewt@redhat.com>
- added patch to prototype llseek

* Tue Jun 17 1997 Erik Troan <ewt@redhat.com>
- built against glibc
