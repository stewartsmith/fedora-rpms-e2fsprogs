%define	_root_sbindir	/sbin
%define	_root_libdir	/%{_lib}

Summary: Utilities for managing the second extended (ext2) filesystem.
Name: e2fsprogs
Version: 1.36
Release: 1.4
License: GPL
Group: System Environment/Base
Source:  ftp://download.sourceforge.net/pub/sourceforge/e2fsprogs/e2fsprogs-%{version}.tar.gz
Source1: http://sourceforge.net/projects/ext2resize/ext2resize-1.1.17.tar.bz2
Patch1: e2fsprogs-1.36-getsize-wrap.patch
Patch9: e2fsprogs-enable-resize.patch
Patch10: ext2resize-cvs-20040419.patch
Patch11: ext2resize-gcc34-fixes.patch
Patch12: ext2resize-printf-format-fixes.patch
Patch13: ext2resize-compiler-warning-fixes.patch
Patch14: ext2resize-canonicalise.patch
Patch19: ext2resize-byteorder.patch
Patch20: ext2resize-nofallback.patch
Patch21: ext2resize-nowrite.patch
Url: http://e2fsprogs.sourceforge.net/
Prereq: /sbin/ldconfig
BuildRoot: %{_tmppath}/%{name}-root
BuildRequires: gettext, texinfo, autoconf, automake

%define ext2resize_basever 1.1.17
%define ext2resize_name ext2resize-%{ext2resize_basever}

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
%setup -q -n e2fsprogs-%{version}
# Fix size-estimations of >=4TB partitions
%patch1 -p1 -b .getsize
# Enable the resize inode by default
%patch9 -p1 -b .resize-on

# Now unpack the ext2resize online resize tarball...
%setup -T -D -q -a 1
# And apply the patches we need for that:
pushd %{ext2resize_name}
# Update to 20040419 ext2resize CVS
%patch10 -p1 -b .cvs
# Fix for gcc34 incompatibilities
%patch11 -p1 -b .gcc34
# Fix printk warnings on 64-bit archs
%patch12 -p1 -b .printf
# Fix misc compiler warnings
%patch13 -p1 -b .warnings
# Canonicalise device names to cope with (eg) LVM symlinks
%patch14 -p1 -b .canon
# Fix byte ordering problems on bigendian hosts
%patch19 -p2 -b .byteorder
# Disable fallback to old-style online resize
%patch20 -p2 -b .nofallback
# Disable the write path used by old-style online
%patch21 -p2 -b .nowrite
popd

%build
%configure --enable-elf-shlibs --enable-nls --disable-e2initrd-helper
# --enable-dynamic-e2fsck
make -C po update-po
make

pushd %{ext2resize_name}
# The byteorder patch adds a new file to the ext2online source tree, so
# we need to rebuild the Makefiles from automake.
aclocal
automake -a -f
# There's a new configure test for byte-order, too.
autoconf
%configure 
make
popd

%install
rm -rf $RPM_BUILD_ROOT
export PATH=/sbin:$PATH
make install install-libs DESTDIR="$RPM_BUILD_ROOT" \
	root_sbindir=%{_root_sbindir} root_libdir=%{_root_libdir}
/sbin/ldconfig -n ${RPM_BUILD_ROOT}%{_libdir}
%find_lang %{name}

pushd %{ext2resize_name}
make DESTDIR=$RPM_BUILD_ROOT install
# For now, we only want to package up the ext2online binary.  Delete the
# others.
rm -f $RPM_BUILD_ROOT%{_sbindir}/ext2resize
rm -f $RPM_BUILD_ROOT%{_sbindir}/ext2prepare
rm -f $RPM_BUILD_ROOT/%{_mandir}/man8/ext2resize*
rm -f $RPM_BUILD_ROOT/%{_mandir}/man8/ext2prepare*
# We want some of the ext2resize doc files to be clearly identified as
# not being part of e2fsprogs!
mv AUTHORS AUTHORS.ext2resize
mv COPYING COPYING.ext2resize
mv NEWS NEWS.ext2resize
mv README README.ext2resize
mv doc/HOWTO doc/HOWTO.ext2resize
popd

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

%files -f %{name}.lang
%defattr(-,root,root)
%doc README RELEASE-NOTES
%doc %{ext2resize_name}/AUTHORS.ext2resize
%doc %{ext2resize_name}/COPYING.ext2resize
%doc %{ext2resize_name}/NEWS.ext2resize
%doc %{ext2resize_name}/README.ext2resize
%doc %{ext2resize_name}/doc/HOWTO.ext2resize

%{_root_sbindir}/badblocks
%{_root_sbindir}/blkid
%{_root_sbindir}/debugfs
%{_root_sbindir}/dumpe2fs
%{_root_sbindir}/e2fsck
%{_root_sbindir}/e2image
%{_root_sbindir}/e2label
%{_root_sbindir}/findfs
%{_root_sbindir}/fsck
%{_root_sbindir}/fsck.ext2
%{_root_sbindir}/fsck.ext3
%{_root_sbindir}/logsave
%{_root_sbindir}/mke2fs
%{_root_sbindir}/mkfs.ext2
%{_root_sbindir}/mkfs.ext3
%{_root_sbindir}/resize2fs
%{_root_sbindir}/tune2fs
%{_sbindir}/filefrag
%{_sbindir}/mklost+found

%{_root_libdir}/libblkid.so.*
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

%{_mandir}/man8/badblocks.8*
%{_mandir}/man8/blkid.8*
%{_mandir}/man8/debugfs.8*
%{_mandir}/man8/dumpe2fs.8*
%{_mandir}/man8/e2fsck.8*
%{_mandir}/man8/findfs.8*
%{_mandir}/man8/filefrag.8*
%{_mandir}/man8/fsck.ext2.8*
%{_mandir}/man8/fsck.ext3.8*
%{_mandir}/man8/e2image.8*
%{_mandir}/man8/e2label.8*
%{_mandir}/man8/fsck.8*
%{_mandir}/man8/logsave.8*
%{_mandir}/man8/mke2fs.8*
%{_mandir}/man8/mkfs.ext2.8*
%{_mandir}/man8/mkfs.ext3.8*
%{_mandir}/man8/mklost+found.8*
%{_mandir}/man8/resize2fs.8*
%{_mandir}/man8/tune2fs.8*

# ext2resize files
%{_sbindir}/ext2online
%{_mandir}/man8/ext2online.8*

%files devel
%defattr(-,root,root)
%{_infodir}/libext2fs.info*
%{_bindir}/compile_et
%{_bindir}/mk_cmds

%{_libdir}/libblkid.a
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
%{_libdir}/pkgconfig/*.pc

%{_datadir}/et
%{_datadir}/ss
%{_includedir}/blkid
%{_includedir}/e2p
%{_includedir}/et
%{_includedir}/ext2fs
%{_includedir}/ss
%{_includedir}/uuid
%{_mandir}/man1/compile_et.1*
%{_mandir}/man1/mk_cmds.1*
%{_mandir}/man3/com_err.3*
%{_mandir}/man3/libblkid.3*
%{_mandir}/man3/uuid.3*
%{_mandir}/man3/uuid_clear.3*
%{_mandir}/man3/uuid_compare.3*
%{_mandir}/man3/uuid_copy.3*
%{_mandir}/man3/uuid_generate.3*
%{_mandir}/man3/uuid_generate_random.3*
%{_mandir}/man3/uuid_generate_time.3*
%{_mandir}/man3/uuid_is_null.3*
%{_mandir}/man3/uuid_parse.3*
%{_mandir}/man3/uuid_time.3*
%{_mandir}/man3/uuid_unparse.3*

%changelog
* Wed Mar 16 2005 Stephen C. Tweedie <sct@redhat.com> 1.36-1.4
- Fix the getsize-wrap patch for >4TB filesystems

* Mon Feb 21 2005 Stephen C. Tweedie <sct@redhat.com> 1.36-1.2
- Re-enable resize2fs
- Add bigendian byte-swapping fix when growing the gdt table

* Fri Feb 11 2005 Stephen C. Tweedie <sct@redhat.com> 1.36-1.1
- Fix for >=4TB devices

* Fri Feb 11 2005 Stephen C. Tweedie <sct@redhat.com> 1.36-1
- Update to e2fsprogs-1.36

* Wed Feb  9 2005 Thomas Woerner <twoerner@redhat.com> 1.35-12
- rebuild

* Wed Dec 22 2004 Stephen C. Tweedie <sct@redhat.com> 
- Disable offline resize for now: resize2fs is incompatible with
  online resize, and can result in corrupt filesystems.

* Thu Dec  9 2004 Stephen C. Tweedie <sct@redhat.com> 
- More byte-order fixes for mke2fs and ext2online
- Disable fallback to old-style resize if new kernel resize code is not
  available

* Mon Nov 15 2004 Stephen C. Tweedie <sct@redhat.com> 
- Fix mke2fs's creation of the resize inode on bigendian hosts

* Tue Oct 19 2004 Thomas Woerner <twoerner@redhat.com> 1.35-11.2
- fixed macroname in changelog (#135413)
- small enhancement of progress patch

* Mon Oct  4 2004 Thomas Woerner <twoerner@redhat.com> 1.35-11.1
- rebuilt

* Fri Sep 17 2004 Thomas Woerner <twoerner@redhat.com> 1.35-11
- extended "-C" option of fsck to pass the file descriptor to the checker
  (#132543)

* Thu Sep 16 2004 Thomas Woerner <twoerner@redhat.com> 1.35-10
- fixed double free in resize2fs (#132707)

* Wed Sep  1 2004 Stephen C. Tweedie <sct@redhat.com> 1.35-9.5
- Add ext2online device name canonicalisation for (eg) LVM symlinks

* Wed Sep  1 2004 Stephen C. Tweedie <sct@redhat.com> 1.35-9.4
- Build and package ext2online during the e2fsprogs build

* Wed Sep  1 2004 Stephen C. Tweedie <sct@redhat.com> 1.35-9.3
- Add ext2resize online resize tools to rpm

* Wed Sep  1 2004 Stephen C. Tweedie <sct@redhat.com> 1.35-9.1.resize.2
- Enable the resize inode by default in mke2fs

* Tue Aug 31 2004 Stephen C. Tweedie <sct@redhat.com> 1.35-9.1.resize.1
- Add initial ext2/3 online resize support

* Sun Aug  8 2004 Alan Cox <alan@redhat.com>
- Close #125316 (buildreq texinfo, gettext)

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Apr  8 2004 Thomas Woerner <twoerner@redhat.com> 1.35-7.1
- fixed 'check after next mount' for filesystems with maximum mount count -1
  (#117109)

* Mon Mar 15 2004 Thomas Woerner <twoerner@redhat.com> 1.35-7
- final 1.35

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Feb  5 2004 Thomas Woerner <twoerner@redhat.com> 1.35-5.1
- C++ header fix for ext2fs.h

* Thu Feb  5 2004 Thomas Woerner <twoerner@redhat.com> 1.35-5
- newest WIP version (2004.01.31)

* Thu Jan 08 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- add patch from Dave Jones

* Sun Dec 14 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.35-WIP-1207

* Fri Nov 14 2003 Phil Knirsch <pknirsch@redhat.com> 1.35-2
- Updated s390 patch. It's not not arch dependant anymore but only changes the
  default blocksizes when necessary.

* Mon Nov 10 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- own /lib/evwms directory  #109583
- build new rpm to get feedback on that snapshot

* Thu Nov 06 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- update the mainframe patch to its current version, but disable it
  until the change also properly supports SCSI and is usable also
  for non-mainframe archs

* Mon Sep 15 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.35-pre
- use ldconfig to create symlinks to shared libs
- remove some cruft from the spec file
- man3 is now part of the devel rpm

* Fri Aug 01 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.34
- do not strip some more apps, should probably just change $(STRIP)...

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu May 08 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.33
- enable translations

* Fri Apr 18 2003 Jeremy Katz <katzj@redhat.com> 1.32-11
- fix error message, do block size checking on s390 only

* Thu Apr 17 2003 Jeremy Katz <katzj@redhat.com> 1.32-10
- check the return code of BLKSSZGET ioctl() to avoid breaking with files

* Tue Apr 15 2003 Phil Knirsch <pknirsch@redhat.com> 1.32-9
- Improved dasd blocksize patch to make it more generic and work correctly.

* Thu Mar 27 2003 Phil Knirsch <pknirsch@redhat.com> 1.32-8
- Removed sync call from e2fsck target. Not needed anymore.

* Wed Mar 26 2003 Phil Knirsch <pknirsch@redhat.com> 1.32-7
- Fixed problem with mke2fs and default blocksize small partitions on dasd
- Disabled Florians patch for now as it's a little incomplete. :-)

* Sun Feb 23 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- add an ugly patch to read full lines of input during e2fsck for /dev/console

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Jan 14 2003 Bill Nottingham <notting@redhat.com> 1.32-2
- do *not* create htree filesystems by default

* Mon Nov 11 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.32

* Fri Nov 01 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.30, leave out already integrated patches
- clean up spec file
- also package some missing files

* Tue Sep 24 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.29, adapt patches to current source

* Sat Aug 10 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- add missing man-pages to filelist

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Fri Jun 21 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- add HTree version of e2fsprogs, disable s390 patch
- add e2fsprogs-dir_index.patch

* Mon Jun 17 2002 Karsten Hopp <karsten@redhat.de>
- set default blocksize for mke2fs on S/390 and zSeries to 4096

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue Apr 09 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- fix further bug in man-page #62995

* Thu Apr 04 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- fix man-pages

* Thu Mar 21 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.27
- patch5 should not be needed anymore

* Fri Mar 08 2002 Elliot Lee <sopwith@redhat.com>
- Make link for mkfs.ext3 (patch5)
- Add man pages for {mkfs,fsck}.{ext2,ext3}

* Tue Feb 19 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.26

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sun Nov 04 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 1.25
- patch for BLKGETSIZE64 is not needed anymore
- adapt autoconf-2.50 patch

* Thu Nov  1 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.23-5
- Make the C++ patch work even with g++ 3.1

* Mon Oct 22 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.23-4
- Fix headers of libext2fs - it wasn't possible to include them from
  C++ code (using private as a variable name isn't a good idea)
- Fix build with autoconf 2.5x

* Mon Sep 17 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- add e2image to filelist

* Wed Aug 29 2001 Bill Nottingham <notting@redhat.com>
- disable BLKGETSIZE64 ioctl support for now

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
- use %%configure to generate config.sub on arm

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
