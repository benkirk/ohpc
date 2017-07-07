#----------------------------------------------------------------------------bh-
# This RPM .spec file is part of the OpenHPC project.
#
# It may have been modified from the default version supplied by the underlying
# release package (if available) in order to apply patches, perform customized
# build/install configurations, and supply additional files to support
# desired integration conventions.
#
#----------------------------------------------------------------------------eh-

# libMesh library that is is dependent on compiler toolchain, MPI, petsc, trilinos

#-ohpc-header-comp-begin-----------------------------

%include %{_sourcedir}/OHPC_macros
%{!?PROJ_DELIM: %global PROJ_DELIM -ohpc}

# OpenHPC convention: the default assumes the gnu toolchain and openmpi
# MPI family; however, these can be overridden by specifing the
# compiler_family and mpi_family variables via rpmbuild or other
# mechanisms.

%{!?compiler_family: %global compiler_family gnu}
%{!?mpi_family:      %global mpi_family openmpi}

# Lmod dependency (note that lmod is pre-populated in the OpenHPC OBS build
# environment; if building outside, lmod remains a formal build dependency).
%if !0%{?OHPC_BUILD}
BuildRequires: lmod%{PROJ_DELIM}
%endif
# Compiler dependencies
BuildRequires: coreutils
%if %{compiler_family} == gnu
BuildRequires: gnu-compilers%{PROJ_DELIM}
Requires:      gnu-compilers%{PROJ_DELIM}
BuildRequires: scalapack-%{compiler_family}-%{mpi_family}%{PROJ_DELIM}
Requires:      scalapack-%{compiler_family}-%{mpi_family}%{PROJ_DELIM}
%endif
%if %{compiler_family} == intel
BuildRequires: gcc-c++ intel-compilers-devel%{PROJ_DELIM}
Requires:      gcc-c++ intel-compilers-devel%{PROJ_DELIM}
%if 0%{?OHPC_BUILD}
BuildRequires: intel_licenses
%endif
%endif

# MPI dependencies
%if %{mpi_family} == impi
BuildRequires: intel-mpi-devel%{PROJ_DELIM}
Requires:      intel-mpi-devel%{PROJ_DELIM}
%endif
%if %{mpi_family} == mvapich2
BuildRequires: mvapich2-%{compiler_family}%{PROJ_DELIM}
Requires:      mvapich2-%{compiler_family}%{PROJ_DELIM}
%endif
%if %{mpi_family} == openmpi
BuildRequires: openmpi-%{compiler_family}%{PROJ_DELIM}
Requires:      openmpi-%{compiler_family}%{PROJ_DELIM}
%endif
%if %{mpi_family} == mpich
BuildRequires: mpich-%{compiler_family}%{PROJ_DELIM}
Requires:      mpich-%{compiler_family}%{PROJ_DELIM}
%endif

#-ohpc-header-comp-end-------------------------------

# Base package name
%define pname libmesh
%define PNAME %(echo %{pname} | tr [a-z] [A-Z])

Name:           %{pname}-%{compiler_family}-%{mpi_family}%{PROJ_DELIM}
Summary:        libMesh
License:        2-clause BSD
Group:          %{PROJ_NAME}/parallel-libs
Version:        1.2.0
Release:        1.0_benkirk

Source0:        https://github.com/libMesh/libmesh/releases/download/v%{version}/libmesh-%{version}.tar.gz
Source1:        OHPC_macros
Source2:        OHPC_setup_compiler
Source3:        OHPC_setup_mpi
#Patch1:         petsc.rpath.patch
Url:            http://libmesh.github.io
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
DocDir:         %{OHPC_PUB}/doc/contrib
BuildRequires:  petsc-%{compiler_family}-%{mpi_family}%{PROJ_DELIM}
BuildRequires:  trilinos-%{compiler_family}-%{mpi_family}%{PROJ_DELIM}
#BuildRequires:  phdf5-%{compiler_family}-%{mpi_family}%{PROJ_DELIM}
BuildRequires:  boost-%{compiler_family}-%{mpi_family}%{PROJ_DELIM}
BuildRequires:  hdf5-devel
BuildRequires:  python
BuildRequires:  valgrind%{PROJ_DELIM}
BuildRequires:  xz
BuildRequires:  zlib-devel
BuildRequires:  tbb-devel
BuildRequires:  eigen3-devel

%include %{_sourcedir}/OHPC_macros
#!BuildIgnore: post-build-checks
%define debug_package %{nil}

# Default library install path
%define install_path %{OHPC_LIBS}/%{compiler_family}/%{mpi_family}/%{pname}/%version

%description
The libMesh library provides a framework for the numerical simulation of partial differential equations using arbitrary unstructured discretizations on serial and parallel platforms. A major goal of the library is to provide support for adaptive mesh refinement (AMR) computations in parallel while allowing a research scientist to focus on the physics they are modeling.

%prep
%setup -q -n %{pname}-%{version}


%build
# OpenHPC compiler/mpi designation
export OHPC_COMPILER_FAMILY=%{compiler_family}
export OHPC_MPI_FAMILY=%{mpi_family}
. %{_sourcedir}/OHPC_setup_compiler
. %{_sourcedir}/OHPC_setup_mpi
module load boost petsc trilinos
module unload hdf5 phdf5

CXX=mpicxx \
CC=mpicc \
FC=mpif90 \
F77=mpif77 \
./configure \
%if %{compiler_family} == gnu7
    --disable-tbb \
%endif
    --with-petsc="${PETSC_DIR}" \
    --with-trilinos="${TRILINOS_DIR}" \
    --with-methods="opt prof" \
    --prefix=%{install_path} || { cat config.log && exit 1; }

%make_build




%install
%make_install

# OpenHPC module file
%{__mkdir} -p %{buildroot}%{OHPC_MODULEDEPS}/%{compiler_family}-%{mpi_family}/%{pname}
%{__cat} << EOF > %{buildroot}/%{OHPC_MODULEDEPS}/%{compiler_family}-%{mpi_family}/%{pname}/%{version}
#%Module1.0#####################################################################

proc ModulesHelp { } {

puts stderr " "
puts stderr "This module loads the libMesh library built with the %{compiler_family} compiler"
puts stderr "toolchain and the %{mpi_family} MPI stack."
puts stderr " "

puts stderr "\nVersion %{version}\n"

}
module-whatis "Name: %{pname} built with %{compiler_family} compiler and %{mpi_family} MPI"
module-whatis "Version: %{version}"
module-whatis "Category: runtime library"
module-whatis "Description: %{summary}"
module-whatis "%{url}"

set     version                     %{version}

# Require phdf5, petsc, trilinos

if [ expr [ module-info mode load ] || [module-info mode display ] ] {
    if {  ![is-loaded phdf5]  } {
        module load phdf5
    }
    if {  ![is-loaded petsc]  } {
        module load petsc
    }
    if {  ![is-loaded trilinos]  } {
        module load trilinos
    }
}

prepend-path    PATH                %{install_path}/bin
prepend-path    INCLUDE             %{install_path}/include
prepend-path    LD_LIBRARY_PATH     %{install_path}/lib

setenv          %{PNAME}_DIR        %{install_path}
setenv          %{PNAME}_BIN        %{install_path}/bin
setenv          %{PNAME}_INC        %{install_path}/include
setenv          %{PNAME}_LIB        %{install_path}/lib

EOF

%{__cat} << EOF > %{buildroot}/%{OHPC_MODULEDEPS}/%{compiler_family}-%{mpi_family}/%{pname}/.version.%{version}
#%Module1.0#####################################################################
##
## version file for %{pname}-%{version}
##
set     ModulesVersion      "%{version}"
EOF

%{__mkdir} -p $RPM_BUILD_ROOT/%{_docdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%{OHPC_HOME}
%{OHPC_PUB}
%doc

%changelog
