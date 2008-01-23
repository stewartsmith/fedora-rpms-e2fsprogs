%define	_root_sbindir	/sbin
%define	_root_libdir	/%{_lib}

Summary: Utilities for managing the second and third extended (ext2/ext3) filesystems
Name: e2fsprogs
Version: 1.40.4
Release: 5%{?dist}
# License based on upstream-modified COPYING file,
# which clearly states "V2" intent.
License: GPLv2
Group: System Environment/Base
Source0: http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
Source1: ext2_types-wrapper.h
Source2: blkid_types-wrapper.h
Source3: uuidd.init
Patch1: e2fsprogs-1.39-blkid-devmapper.patch
Patch2: e2fsprogs-1.38-etcblkid.patch
Patch3: e2fsprogs-1.39-mkinstalldirs.patch
Patch4: e2fsprogs-1.40.4-uuidd-tidy.patch
Patch5: e2fsprogs-1.40.4-sb_feature_check_ignore.patch
Patch6: e2fsprogs-1.40.4-blkid-ext4dev.patch

Url: http://e2fsprogs.sourceforge.net/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires: e2fsprogs-libs = %{version}-%{release}, device-mapper
BuildRequires: gettext, texinfo, autoconf, automake >= 1.10, libselinux-devel
BuildRequires: libsepol-devel, gettext-devel, pkgconfig
BuildRequires: device-mapper-devel gawk

%description
The e2fsprogs package contains a number of utilities for creating,
checking, modifying, and correcting any inconsistencies in second
and third extended (ext2/ext3) filesystems. E2fsprogs contains
e2fsck (used to repair filesystem inconsistencies after an unclean
shutdown), mke2fs (used to initialize a partition to contain an
empty ext2 filesystem), debugfs (used to examine the internal
structure of a filesystem, to manually repair a corrupted
filesystem, or to create test cases for e2fsck), tune2fs (used to
modify filesystem parameters), and most of the other core ext2fs
filesystem utilities.

You should install the e2fsprogs package if you need to manage the
performance of an ext2 and/or ext3 filesystem.

%package libs
Summary: Ext2/3 filesystem-specific shared libraries and headers
Group: Development/Libraries
# License based on upstream-modified COPYING file,
# which clearly states "V2" intent as well as other
# licenses for various libs, which also have in-source specification.
License: GPLv2 and LGPLv2 and BSD and MIT
Requires(post): /sbin/ldconfig

%description libs
E2fsprogs-lib contains the libraries of the e2fsprogs package.

%package devel
Summary: Ext2/3 filesystem-specific static libraries and headers
Group: Development/Libraries
# License based on upstream-modified COPYING file,
# which clearly states [L]GPLv2 intent as well as other
# licenses for various libs, which also have in-source specification.
License: GPLv2 and LGPLv2 and BSD and MIT
Requires: e2fsprogs-libs = %{version}-%{release}
Requires: device-mapper-devel >= 1.02.02-3
Requires: gawk
Requires(post): /sbin/install-info
Requires(postun): /sbin/install-info

%description devel
E2fsprogs-devel contains the libraries and header files needed to
develop second and third extended (ext2/ext3) filesystem-specific
programs.

You should install e2fsprogs-devel if you want to develop ext2/ext3
filesystem-specific programs. If you install e2fsprogs-devel, you'll
also want to install e2fsprogs.

%package -n uuidd
Summary: helper daemon to guarantee uniqueness of time-based UUIDs
Group: System Environment/Daemons
Requires: e2fsprogs-libs = %{version}-%{release}
License: GPLv2
Requires(pre): shadow-utils

%description -n uuidd
The uuidd package contains a userspace daemon (uuidd) which guarantees
uniqueness of time-based UUID generation even at very high rates on
SMP systems.

%prep
%setup -q -n e2fsprogs-%{version}
# look at device mapper devices
%patch1 -p1 -b .dm
# put blkid.tab in /etc/blkid/
%patch2 -p1 -b .etcblkid
# Fix for newer autoconf (#220715)
%patch3 -p1 -b .mkinstalldirs
# uuidd manpage tidyup
%patch4 -p1 -b .uuidd-tidy
# ignore some flag differences on primary/backup sb feature checks
%patch5 -p1 -b .featurecheck
# teach blkid about ext4dev, for now
%patch6 -p1 -b .ext4-blkid

%build
aclocal
autoconf
%configure --enable-elf-shlibs --enable-nls --disable-e2initrd-helper  --enable-blkid-devmapper --enable-blkid-selinux --enable-dynamic-e2fsck
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
export PATH=/sbin:$PATH
make install install-libs DESTDIR=$RPM_BUILD_ROOT INSTALL="%{__install} -p" \
	root_sbindir=%{_root_sbindir} root_libdir=%{_root_libdir}

# ugly hack to allow parallel install of 32-bit and 64-bit -devel packages:
mv -f $RPM_BUILD_ROOT%{_includedir}/ext2fs/ext2_types.h \
      $RPM_BUILD_ROOT%{_includedir}/ext2fs/ext2_types-%{_arch}.h
install -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_includedir}/ext2fs/ext2_types.h

mv -f $RPM_BUILD_ROOT%{_includedir}/blkid/blkid_types.h \
      $RPM_BUILD_ROOT%{_includedir}/blkid/blkid_types-%{_arch}.h
install -p -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_includedir}/blkid/blkid_types.h

# Our own initscript for uuidd
install -m 755 %{SOURCE3} $RPM_BUILD_ROOT/etc/init.d/uuidd
# And a dir uuidd needs that the makefiles don't create
install -d $RPM_BUILD_ROOT/var/lib/libuuid

%find_lang %{name}

%check
make check

%clean
rm -rf %{buildroot}

%post
[ -e /etc/blkid.tab ] && mv /etc/blkid.tab /etc/blkid/blkid.tab || :
[ -e /etc/blkid.tab.old ] && mv /etc/blkid.tab.old /etc/blkid/blkid.tab.old || :

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

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

%pre -n uuidd
getent group uuidd >/dev/null || groupadd -r uuidd
getent passwd uuidd >/dev/null || \
useradd -r -g uuidd -d /var/lib/libuuid -s /sbin/nologin \
    -c "UUID generator helper daemon" uuidd
exit 0

%post -n uuidd
/sbin/chkconfig --add uuidd

%preun -n uuidd
if [ "$1" = 0 ]
then
	/sbin/service uuidd stop > /dev/null 2>&1 || :
	/sbin/chkconfig --del uuidd
fi

%files -f %{name}.lang
%defattr(-,root,root)
%doc README RELEASE-NOTES

%dir /etc/blkid
%config(noreplace) /etc/mke2fs.conf
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

%{_bindir}/chattr
%{_bindir}/lsattr
%{_bindir}/uuidgen
%{_mandir}/man1/chattr.1*
%{_mandir}/man1/lsattr.1*
%{_mandir}/man1/uuidgen.1*

%{_mandir}/man5/e2fsck.conf.5*
%{_mandir}/man5/mke2fs.conf.5*

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

%files libs
%defattr(-,root,root)
%{_root_libdir}/libblkid.so.*
%{_root_libdir}/libcom_err.so.*
%{_root_libdir}/libe2p.so.*
%{_root_libdir}/libext2fs.so.*
%{_root_libdir}/libss.so.*
%{_root_libdir}/libuuid.so.*

%files devel
%defattr(-,root,root)
%{_infodir}/libext2fs.info*
%{_bindir}/compile_et
%{_bindir}/mk_cmds

%{_libdir}/libblkid.a
%{_libdir}/libblkid.so
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

%files -n uuidd
%defattr(-,root,root)
/etc/init.d/uuidd
%{_mandir}/man8/uuidd.8*
%attr(-, uuidd, uuidd) %{_sbindir}/uuidd
%dir %attr(2775, uuidd, uuidd) /var/lib/libuuid

%changelog
* Wed Jan 23 2008 Eric Sandeen <sandeen@redhat.com> 1.40.4-5
- ignore some primary/backup superblock flag differences (#428893)
- teach libblkid about ext4dev

* Mon Jan 10 2008 Eric Sandeen <sandeen@redhat.com> 1.40.4-4
- Build e2fsck as a dynamically linked binary.
- Re-fix uidd manpage default paths.

* Tue Jan 09 2008 Eric Sandeen <sandeen@redhat.com> 1.40.4-3
- New uuidd subpackage, and properly set up uuidd at install.

* Tue Jan 01 2008 Eric Sandeen <esandeen@redhat.com> 1.40.4-2
- Add new uidd files to specfile

* Tue Jan 01 2008 Eric Sandeen <esandeen@redhat.com> 1.40.4-1
- New upstream version, drop several now-upstream patches.

* Tue Jan 01 2008 Eric Sandeen <esandeen@redhat.com> 1.40.2-15
- Drop resize_inode removal patch from tune2fs; ostensibly was
  for old kernels which could not mount, but seems to be fine.
- Drop pottcdate removal patch, and don't rebuild .po files,
  causes multilib problems and we generally shouldn't rebuild.
- Drop multilib patch; wrapper header should take care of this now.
- Drop ->open rename, Fedora seems ok with this now.

* Tue Dec 11 2007 Eric Sandeen <esandeen@redhat.com> 1.40.2-14
- Fix integer overflows (#414591 / CVE-2007-5497)

* Tue Dec  4 2007 Stepan Kasal <skasal@redhat.com> 1.40.2-13
- The -devel package now requires device-mapper-devel, to match
  the dependency in blkid.pc (#410791)

* Tue Nov 27 2007 Eric Sandeen <esandeen@redhat.com> 1.40.2-12
- Use upstream patch for blkid fat detection, avoids div-by-zero
  when encountering some BSD partitions (#398281)

* Tue Oct 23 2007 Eric Sandeen <esandeen@redhat.com> 1.40.2-11
- Add arm to multilib header wrapper

* Sat Oct 20 2007 Eric Sandeen <esandeen@redhat.com> 1.40.2-10
- Make (more) file timestamps match those in tarball for multilib tidiness 
- Fix e2fsprogs-libs summary (shared libs not static)

* Tue Oct 15 2007 Eric Sandeen <esandeen@redhat.com> 1.40.2-9
- Detect big-endian squashfs filesystems in libblkid (#305151)

* Tue Oct 02 2007 Eric Sandeen <esandeen@redhat.com> 1.40.2-8
- Detect squashfs filesystems in libblkid (#305151)

* Tue Sep 18 2007 Eric Sandeen <esandeen@redhat.com> 1.40.2-7
- Fix blkid fat probe when there is a real MBR (#290951)

* Tue Sep 18 2007 Oliver Falk <oliver@linux-kernel.at> 1.40.2-6
- Add alpha to the header wrappers 

* Fri Sep 07 2007 Eric Sandeen <esandeen@redhat.com> 1.40.2-5
- wrap a couple headers to fix multilib issues (#270441)

* Wed Aug 29 2007 Eric Sandeen <esandeen@redhat.com> 1.40.2-4
- add gawk to e2fsprogs-devel Requires, compile_et needs it (#265961)

* Thu Aug 23 2007 Eric Sandeen <esandeen@redhat.com> 1.40.2-3
- Update license tags
- Fix one open-create caller with no mode
- Protect ->open ops from glibc open-create-mode-checker
- Fix source URL
- Add gawk to BuildRequires

* Wed Jul 18 2007 Eric Sandeen <esandeen@redhat.com> 1.40.2-2
- Fix bug in ext2fs_swap_inode_full() on big-endian boxes

* Tue Jul 17 2007 Eric Sandeen <esandeen@redhat.com> 1.40.2-1
- New version 1.40.2
- Fix up warning in badblocks

* Mon Jun 25 2007 Eric Sandeen <esandeen@redhat.com> 1.39-15
- Fix up .po files to remove timestamps; multilib issues (#245653)

* Fri Jun 22 2007 Eric Sandeen <esandeen@redhat.com> 1.39-14
- Many coverity-found potential leaks, segfaults, etc (#239354)
- Fix debugfs segfaults when no fs open (#208416, #209330)
- Avoid recursive loops in logdump due to symlinks in /dev (#210371)
- Don't write changes to the backup superblocks by default (#229561)
- Correct byteswapping for fast symlinks with xattrs (#232663)
- e2fsck: added sanity check for xattr validation (#230193)

* Wed Jun 20 2007 Eric Sandeen <esandeen@redhat.com> 1.39-13
- add dist tag to release field

* Wed Jun 20 2007 Eric Sandeen <esandeen@redhat.com> 1.39-12
- add LUKS support to libblkid (#242421)

* Fri Feb 23 2007 Karsten Hopp <karsten@redhat.com> 1.39-11
- fix post/preun requirements
- use smp flags

* Mon Feb 05 2007 Alasdair Kergon <agk@redhat.com> - 1.39-10
- Add build dependency on new device-mapper-devel package.

* Mon Dec 25 2006 Thomas Woerner <twoerner@redhat.com> - 1.39-9
- build fixes for new automake 1.10 (#220715)

* Mon Dec 18 2006 Thomas Woerner <twoerner@redhat.com> - 1.39-8
- make uuid_generate_time generate unique uuids (#218606)

* Wed Sep 20 2006 Jarod Wilson <jwilson@redhat.com> - 1.39-7
- 32-bit 16T fixups from esandeen (#202807)
- Update summaries and descriptions

* Sun Sep 17 2006 Karel Zak <kzak@redhat.com> - 1.39-6
- Fix problem with empty FAT label (#206656)

* Tue Sep  5 2006 Peter Jones <pjones@redhat.com> - 1.39-5
- Fix memory leak in device probing.

* Mon Jul 24 2006 Thomas Woerner <twoerner@redhat.com> - 1.39-4
- fixed multilib devel conflicts (#192665)

* Thu Jul 20 2006 Bill Nottingham <notting@redhat.com> - 1.39-3
- prevent libblkid returning /dev/dm-X

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.39-2.1
- rebuild

* Mon Jul 10 2006 Karel Zak <kzak@redhat.com> - 1.39-2
- add GFS abd GFS2 support to libblkid

* Thu Jul  6 2006 Thomas Woerner <twoerner@redhat.com> - 1.39-1
- new version 1.39
- dropped ext2online, because resize2fs is now able to do online resize
- spec file cleanup
- enabled checks for build

* Tue Jun 13 2006 Bill Nottingham <notting@redhat.com> - 1.38-15
- prevent libblkid returning /dev/dm-X
- fix build

* Tue Mar 21 2006 Karel Zak <kzak@redhat.com> - 1.38-14
- prevent error messages to stderr caused by libblkid calling libdevmapper

* Mon Mar 13 2006 Karel Zak <kzak@redhat.com>  - 1.38-13
- used upstream version of the blkid-epoch patch (by Theodore Tso, #182188)

* Wed Mar  8 2006 Peter Jones <pjones@redhat.com> - 1.38-12
- Move /etc/blkid.tab to /etc/blkid/blkid.tab

* Tue Mar  7 2006 David Cantrell <dcantrell@redhat.com> - 1.38-11
- BuildRequires pkgconfig

* Tue Mar  7 2006 David Cantrell <dcantrell@redhat.com> - 1.38-10
- Disable /etc/blkid.tab caching if time is set before epoch (#182188)

* Fri Feb 24 2006 Peter Jones <pjones@redhat.com> - 1.38-9
- _don't_ handle selinux context on blkid.tab, dwalsh says this is a no-no.

* Wed Feb 22 2006 Peter Jones <pjones@redhat.com> - 1.38-8
- handle selinux context on blkid.tab

* Mon Feb 20 2006 Karsten Hopp <karsten@redhat.de> 1.38-7
- BuildRequires: gettext-devel

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.38-6.2
- bump again for double-long bug on ppc(64)

* Tue Feb  7 2006 Jesse Keating <jkeating@redhat.com> - 1.38-6.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Wed Jan 11 2006 Karel Zak <kzak@redhat.com> 1.38-6
- cleanup device-mapper patch
- use pkg-config for device-mapper

* Mon Jan  9 2006 Peter Jones <pjones@redhat.com> 1.38-5
- fix some more minor logic errors in dm probing

* Wed Jan  4 2006 Peter Jones <pjones@redhat.com> 1.38-4
- fix a logic error in dm probing
- add priority group for dm devices, so they'll be preferred

* Tue Jan  3 2006 Peter Jones <pjones@redhat.com> 1.38-3
- added support for device-mapper devices

* Fri Dec  9 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Nov 10 2005 Thomas Woerner <twoerner@redhat.com> 1.38-2.1
- fixed file conflicts between 32bit and 64bit packages (#168815)
- fixed mklost+found crashes with buffer overflow (#157773)
  Thanks to Arjan van de Ven for the patch

* Wed Nov  9 2005 Thomas Woerner <twoerner@redhat.com> 1.38-2
- splitted up libs from main package, into a new e2fsprogs-libs package
- fixed requires and prereqs

* Thu Sep  8 2005 Thomas Woerner <twoerner@redhat.com> 1.38-1
- new version 1.38
- Close File descriptor for unregognized devices (#159878)
  Thanks to David Milburn for the patch.
  Merged from RHEL-4
- enable tune2fs to set and clear feature resize_inode (#167816)
- removed outdated information from ext2online man page (#164383)

* Mon Sep  5 2005 Karel Zak <kzak@redhat.com> - 1.37-5
- fix swsuspend partition detection (#165863)
- fix revalidate from ext2 to ext3 (#162927)
- fix vfat without magic detection (#161873)

* Tue May 10 2005 Jeremy Katz <katzj@redhat.com> - 1.37-4
- added libblkid.so to devel package

* Wed May  4 2005 Jeremy Katz <katzj@redhat.com> - 1.37-3
- fix cramfs detection bug in libblkid

* Fri Apr  8 2005 Thomas Woerner <twoerner@redhat.com> 1.37-2
- upstream fixes 1.1589, 1.1590 and 1.1591:
- add include of stdlib.h to fix a core dump bug on IA64
- ignore environment variables in blkid and ext2fs for setuid and setguid
  programs
- no LOW_DTIME checks if the superblock last mount time looks insane

* Fri Apr  8 2005 Thomas Woerner <twoerner@redhat.com> 1.37-1
- new version 1.37
- dropped upstream merged getsize-wrap patch

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
