# Make Pod from Scratch

## 1. Create quarantine process by using chroot

```bash
# Create a directory for the quarantine process
mkdir -p /home/namespace/box

# Create /bin, /lib, /lib64 for the quarantine process
mkdir -p /home/namespace/box/{bin,lib,lib64}

# Copy the binaries and libraries for the quarantine process
cp -v /usr/bin/kill /home/namespace/box/bin/
cp -v /usr/bin/ps /home/namespace/box/bin/
cp -v /usr/bin/bash /home/namespace/box/bin/
cp -v /usr/bin/ls /home/namespace/box/bin/

# copy library dependencies to the quarantine process's lib directory
cp -r /lib/* /home/namespace/box/lib/
cp -r /lib64/* /home/namespace/box/lib64/

# mount the proc directory to the quarantine process
mount -t proc proc /home/namespace/box/proc

# chroot to the quarantine process
chroot /home/namespace/box /bin/bash
```

## 2. Use mount to provide process data to the quarantine process

```bash
# mount the data directory to the quarantine process
mount --bind /tmp/ /home/namespace/box/data
```

## 3. Use unshare to keep the quarantine process in a separate namespace

```bash
# unshare the quarantine process
unshare -p -f --mount-proc=/home/namespace/box/proc chroot /home/namespace/box /bin/bash
```

The main reason to use `unshare` is to keep the quarantine process in a separate namespace.
If we do not use the unshare command, the quarantine process will be in the same namespace as the parent process.
This means that the quarantine process will be able to see the processes of the parent process, which indicates that the quarantine process is not isolated.
As the process is not isolates, we could kill the parent process from the quarantine process, which could lead to CVE(common vulnerabilities and exposures).

## 4. Create network namespace for the quarantine process

```bash
# unshare the quarantine process with network namespace
unshare -p -n -f --mount-proc=/home/namespace/box/proc chroot /home/namespace/box /bin/bash
```

This time, we use the `-n` option to create a network namespace for the quarantine process.
If we do not use the `-n` option, the quarantine process will be in the same network namespace as the parent process.

## 5. Use cgroup to control CPU and memory usage of the quarantine process

```bash
# create a cgroup for the quarantine process
mkdir -p /sys/fs/cgroup/cpu/namespace
mkdir -p /sys/fs/cgroup/memory/namespace

# limit the CPU usage of the quarantine process
echo 100000 > /sys/fs/cgroup/cpu/namespace/cpu.cfs_quota_us

# limit the memory usage of the quarantine process
echo 100000000 > /sys/fs/cgroup/memory/namespace/memory.limit_in_bytes

# move the quarantine process to the cgroup
echo <PID> > /sys/fs/cgroup/cpu/namespace/tasks
echo <PID> > /sys/fs/cgroup/memory/namespace/tasks
```
