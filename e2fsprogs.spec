%define	_root_sbindir	/sbin
%define	_root_libdir	/%{_lib}

Summary: Utilities for managing the second and third extended (ext2/ext3) filesystems
Name: e2fsprogs
Version: 1.41
Release: 0.1.WIP.0707{?dist}
# License based on upstream-modified COPYING file,
# which clearly states "V2" intent.
License: GPLv2
Group: System Environment/Base
Source0: http://downloads.sourceforge.net/%{name}/%{name}-%{version}-WIP-0707.tar.gz
Source1: ext2_types-wrapper.h
Source2: blkid_types-wrapper.h
Source3: uuidd.init
Patch1: e2fsprogs-1.38-etcblkid.patch
Patch2: e2fsprogs-1.40.4-sb_feature_check_ignore.patch

Url: http://e2fsprogs.sourceforge.net/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires: e2fsprogs-libs = %{version}-%{release}, device-mapper
BuildRequires: pkgconfig, texinfo, libselinux-devel
BuildRequires: libsepol-devel, device-mapper-devel, util-linux

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
Requires(preun): /sbin/install-info

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
# put blkid.tab in /etc/blkid/
%patch1 -p1 -b .etcblkid
# ignore some flag differences on primary/backup sb feature checks
# mildly unsafe but 'til I get something better, avoid full fsck
# after an selinux install...
%patch2 -p1 -b .featurecheck

%build
%configure --enable-elf-shlibs --enable-nls --disable-e2initrd-helper  --enable-blkid-devmapper --enable-blkid-selinux
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
export PATH=/sbin:$PATH
make install install-libs DESTDIR=$RPM_BUILD_ROOT INSTALL="%{__install} -p" \
	root_sbindir=%{_root_sbindir} root_libdir=%{_root_libdir}

# ugly hack to allow parallel install of 32-bit and 64-bit -devel packages:
%define multilib_arches %{ix86} x86_64 ppc ppc64 s390 s390x sparcv9 sparc64

%ifarch %{multilib_arches}
mv -f $RPM_BUILD_ROOT%{_includedir}/ext2fs/ext2_types.h \
      $RPM_BUILD_ROOT%{_includedir}/ext2fs/ext2_types-%{_arch}.h
install -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_includedir}/ext2fs/ext2_types.h

mv -f $RPM_BUILD_ROOT%{_includedir}/blkid/blkid_types.h \
      $RPM_BUILD_ROOT%{_includedir}/blkid/blkid_types-%{_arch}.h
install -p -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_includedir}/blkid/blkid_types.h
%endif

# Our own initscript for uuidd
install -D -m 755 %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/uuidd
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
/sbin/install-info %{_infodir}/libext2fs.info.gz %{_infodir}/dir || :

%preun devel
if [ $1 = 0 ]; then
   /sbin/install-info --delete %{_infodir}/libext2fs.info.gz %{_infodir}/dir || :
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
%{_root_sbindir}/e2undo
%{_root_sbindir}/findfs
%{_root_sbindir}/fsck
%{_root_sbindir}/fsck.ext2
%{_root_sbindir}/fsck.ext3
%{_root_sbindir}/fsck.ext4
%{_root_sbindir}/fsck.ext4dev
%{_root_sbindir}/logsave
%{_root_sbindir}/mke2fs
%{_root_sbindir}/mkfs.ext2
%{_root_sbindir}/mkfs.ext3
%{_root_sbindir}/mkfs.ext4
%{_root_sbindir}/mkfs.ext4dev
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
%{_mandir}/man8/fsck.ext4.8*
%{_mandir}/man8/fsck.ext4dev.8*
%{_mandir}/man8/e2image.8*
%{_mandir}/man8/e2label.8*
%{_mandir}/man8/e2undo.8*
%{_mandir}/man8/fsck.8*
%{_mandir}/man8/logsave.8*
%{_mandir}/man8/mke2fs.8*
%{_mandir}/man8/mkfs.ext2.8*
%{_mandir}/man8/mkfs.ext3.8*
%{_mandir}/man8/mkfs.ext4.8*
%{_mandir}/man8/mkfs.ext4dev.8*
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
/etc/rc.d/init.d/uuidd
%{_mandir}/man8/uuidd.8*
%attr(-, uuidd, uuidd) %{_sbindir}/uuidd
%dir %attr(2775, uuidd, uuidd) /var/lib/libuuid

%changelog
* Mon Jul 07 2008 Eric Sandeen <sandeen@redhat.com> 1.41-0.1.WIP.0707
- New upstream snapshot release

* Fri Jun 20 2008 Eric Sandeen <sandeen@redhat.com> 1.41-0.WIP.0617.1
- Fix blkid -g segfault when clearing entries (#452333)

* Wed Jun 18 2008 Eric Sandeen <sandeen@redhat.com> 1.41-0.WIP.0617
- New upstream snapshot release for ext4 capability

* Wed Jun 04 2008 Eric Sandeen <sandeen@redhat.com> 1.40.10-3
- Tidy up multilib hack for non-multilib arches (#446016)
- Fix up %postun script (#449868)

* Wed Jun 04 2008 Dennis Gilmore <dennis@ausil.us> 1.40.10-2
- setup header support for sparc

* Fri May 23 2008 Eric Sandeen <esandeen@redhat.com> 1.40.10-1
- New upstream version
- Fixes unprivileged blkid use problem (#448591)

* Mon May 12 2008 Eric Sandeen <esandeen@redhat.com> 1.40.9-2
- Fix blkid swap recognition on big-endian boxes (#445786)

* Sun Apr 27 2008 Eric Sandeen <esandeen@redhat.com> 1.40.9-1
- New upstream version

* Fri Mar 14 2008 Eric Sandeen <esandeen@redhat.com> 1.40.8-2
- Update ext2fs_swap_inode_full() fix to match upstream
- Check more of swapv1 header in blkid detection (#442937)

* Fri Mar 14 2008 Eric Sandeen <esandeen@redhat.com> 1.40.8-1
- New upstream version

* Mon Mar 03 2008 Eric Sandeen <esandeen@redhat.com> 1.40.7-2
- second try at fixing resize2fs vs. large inodes... (#434893)

* Fri Feb 29 2008 Eric Sandeen <esandeen@redhat.com> 1.40.7-1
- New upstream version, special leap-day edition
- Fix resize2fs losing inline xattrs when shrinking (#434893)
  and add patch to fix swap_inode_full in this case
- Allow mke2fs & tune2fs to manipulate large_file feature (#258381)
- Handle lvm error conditions in libblkid (#433857)
- Allow tune2fs to clear the resize_inode feature (#167816)
- Teach blkid to detect LVM2 physical volumes (#409321)
- Show "mostly printable" xattrs as text in debugfs (#430621)
- Trimmed pre-1.38 rpm changelog entries

* Sun Feb 10 2008 Eric Sandeen <esandeen@redhat.com> 1.40.6-1
- New upstream version

* Fri Feb 08 2008 Eric Sandeen <esandeen@redhat.com> 1.40.5-2
- gcc-4.3 rebuild

* Mon Jan 28 2008 Eric Sandeen <esandeen@redhat.com> 1.40.5-1
- New upstream version, drop several now-upstream patches.

* Thu Jan 24 2008 Eric Sandeen <sandeen@redhat.com> 1.40.4-7
- Fix sb flag comparisons properly this time (#428893)
- Make 256-byte inodes for the [default] mkfs case.
  This will facilitate upgrades to ext4 later, and help xattr perf.

* Wed Jan 23 2008 Eric Sandeen <sandeen@redhat.com> 1.40.4-6
- Completely clobber e2fsck.static build.

* Wed Jan 23 2008 Eric Sandeen <sandeen@redhat.com> 1.40.4-5
- Ignore some primary/backup superblock flag differences (#428893)
- Teach libblkid about ext4dev.

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

