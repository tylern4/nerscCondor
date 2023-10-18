# nerscCondor

## Setting up HTCondor

Download newsest pre-compiled version of HTCondor built for [Centos8](https://research.cs.wisc.edu/htcondor/tarball/current).

```bash
wget https://research.cs.wisc.edu/htcondor/tarball/current/9.11.2/release/condor-9.11.2-x86_64_CentOS8-stripped.tar.gz
tar -xvf condor-9.11.2-x86_64_CentOS8-stripped.tar.gz
export CONDOR_INSTALL=/path/to/condor
export PATH=${CONDOR_INSTALL}/bin:${CONDOR_INSTALL}/sbin:$PATH
```

## Using scrontab to start htcondor




## Setting up pegasus

Download newsest pre-compiled version of pegagsus built for [rhel8](http://download.pegasus.isi.edu/pegasus).

```bash
wget http://download.pegasus.isi.edu/pegasus/5.0.2/pegasus-binary-5.0.2-x86_64_rhel_8.tar.gz
tar -xvf pegasus-binary-5.0.2-x86_64_rhel_8.tar.gz
export PATH=/path/to/pegasus/bin:$PATH
```

### Create conda environment

```bash
conda create -n pegasus python=3.10
conda activate pegasus
conda install -c conda-forge pegasus-wms
```

### Configuring to work with slurm

- [ ] run pegasus command to put files in right place
- [ ] also put them in `~/.blah`
- [ ] `~/.blah/user.config` > `blah_debug_save_submit_info=/path/to/slurmjobs` to look at slurm jobs

'site.yml' doesn't work. Needs to be modified to use `globus: totalmemory` or better is to figure out when `/global/common/software/m3792/htcondor-9.11.2/libexec/blahp/slurm_submit.sh` and modify the memory (and out and err files) before submitting.

