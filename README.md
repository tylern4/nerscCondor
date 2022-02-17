# nerscCondor

 Notes on HTCondor running at NERSC

### Spin Configuration

```

```

### Building htcondor on cori

```bash
module swap PrgEnv-intel PrgEnv-gnu;
export CC=$(which gcc); export CXX=$(which g++);
```

```bash
git clone -b V9_5_0 https://github.com/htcondor/htcondor.git htcondor-github
mkdir -p htcondor-github/compile
cd htcondor-github/compile
```

patch 1:
```patch
diff --git a/build/cmake/CondorPackageConfig.cmake b/build/cmake/CondorPackageConfig.cmake
index fffd51887f..4494721e73 100644
--- a/build/cmake/CondorPackageConfig.cmake
+++ b/build/cmake/CondorPackageConfig.cmake
@@ -174,6 +174,11 @@ if ( ${OS_NAME} STREQUAL "LINUX" )
                set( EXTERNALS_RPATH "$ORIGIN/../lib:/lib64:/usr/lib64:$ORIGIN/../lib/condor:/usr/lib64/condor" )
         if ( ${SYSTEM_NAME} MATCHES "rhel7" OR ${SYSTEM_NAME} MATCHES "centos7" OR ${SYSTEM_NAME} MATCHES "sl7")
             set( PYTHON_RPATH "$ORIGIN/../../:/usr/lib64/boost169:/lib64:/usr/lib64:$ORIGIN/../../condor" )
+        elseif(${SYSTEM_NAME} MATCHES "suse")
+            message(STATUS "OS: SUSE")
+            set( CONDOR_RPATH "$ORIGIN/../lib:/lib:/usr/lib:/lib64:$ORIGIN/../lib/condor:/usr/lib/condor" )
+            set( EXTERNALS_RPATH "$ORIGIN/../lib:/lib:/usr/lib:/lib64:$ORIGIN/../lib/condor:/usr/lib/condor" )
+            set( PYTHON_RPATH "$ORIGIN/../../:/lib:/lib64:/usr/lib:$ORIGIN/../../condor" )
         else()
             set( PYTHON_RPATH "$ORIGIN/../../:/lib64:/usr/lib64:$ORIGIN/../../condor" )
         endif()
```

patch 2:
```patch
diff --git a/src/blahp/CMakeLists.txt b/src/blahp/CMakeLists.txt
index 6ea15d2de6..dafc4ac3d3 100644
--- a/src/blahp/CMakeLists.txt
+++ b/src/blahp/CMakeLists.txt
@@ -65,6 +65,6 @@ endif(NOT CONDOR_PACKAGE_NAME)
 if (NOT CONDOR_PACKAGE_NAME OR WITH_BLAHP)
     add_subdirectory(src build)
     add_subdirectory(config)
-    add_subdirectory(doc)
+    # add_subdirectory(doc)
 endif(NOT CONDOR_PACKAGE_NAME OR WITH_BLAHP)

```


```bash
# Maybe overkill with options
cmake -DHAVE_BACKFILL:BOOL=TRUE -DHAVE_BOINC:BOOL=FALSE -DHAVE_KBDD:BOOL=TRUE -DHAVE_HIBERNATION:BOOL=TRUE -DWANT_CONTRIB:BOOL=ON -DWANT_MAN_PAGES:BOOL=FALSE -DWANT_GLEXEC:BOOL=FALSE -D_VERBOSE:BOOL=TRUE -DWITH_GLOBUS:BOOL=FALSE -DWITH_VOMS:BOOL=FALSE -DCMAKE_INSTALL_PREFIX:PATH=/global/common/software/m3792/htcondor -DSYSTEM_NAME=suse -DWITH_SCITOKENS:BOOL=FALSE -DWANT_PYTHON2_BINDINGS:BOOL=FALSE -DWANT_PYTHON3_BINDINGS:BOOL=FALSE -DWITH_PYTHON_BINDINGS:BOOL=FALSE -DBUILD_TESTING:BOOL=FALSE -DWANT_MAN_PAGES:BOOL=FALSE ..


```

### Building htcondor on perlmutter?

First look seems to say cori build works on perlmutter...

If not, do patch #2 and build with:

```bash
module swap PrgEnv-nvidia/8.2.0 PrgEnv-gnu;
export CC=$(which gcc); export CXX=$(which g++);
```

```bash

cmake -DHAVE_BACKFILL:BOOL=TRUE -DHAVE_BOINC:BOOL=FALSE -DHAVE_KBDD:BOOL=TRUE -DHAVE_HIBERNATION:BOOL=TRUE -DWANT_CONTRIB:BOOL=ON -DWANT_MAN_PAGES:BOOL=FALSE -DWANT_GLEXEC:BOOL=FALSE -D_VERBOSE:BOOL=TRUE -DWITH_GLOBUS:BOOL=FALSE -DWITH_VOMS:BOOL=FALSE -DCMAKE_INSTALL_PREFIX:PATH=/global/common/software/m3792/htcondor -DSYSTEM_NAME=suse -DWITH_SCITOKENS:BOOL=FALSE -DWANT_PYTHON2_BINDINGS:BOOL=FALSE -DWANT_PYTHON3_BINDINGS:BOOL=FALSE -DWITH_PYTHON_BINDINGS:BOOL=FALSE -DBUILD_TESTING:BOOL=FALSE -DWANT_MAN_PAGES:BOOL=FALSE -DWITH_KRB5:BOOL=FALSE ..

```

###  Anything else?

cleanup:

`kill $(ps aux | grep -v grep | grep -i condor_master | awk '{print $2}')`

