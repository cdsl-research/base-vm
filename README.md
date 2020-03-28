# base-vm

- Kea v1.6.2
- DRBD DrbdMon v9.12.0

## [1] DRBD Setup

```
# Host define
echo -e "\n192.168.100.13 base-m \n192.168.100.14 base-j" | sudo tee -a /etc/hosts

# Add packages
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:linbit/linbit-drbd9-stack
sudo apt install -y drbd-dkms drbd-utils lvm2
sudo apt install -y linstor-controller linstor-satellite  linstor-client

# Enable Service
sudo systemctl enable --now linstor-controller
sudo systemctl start linstor-controller

# Check node status
linstor node list
╭─────────────────────────────────────╮
┊ Node ┊ NodeType ┊ Addresses ┊ State ┊
╞═════════════════════════════════════╡
╰─────────────────────────────────────╯

# Set Controller
cat <<EOF | sudo tee /etc/linstor/linstor-client.conf
[global]
controllers=base-m,base-j
EOF

cat /etc/linstor/linstor-client.conf
linstor node create `hostname` `hostname -I`

sudo systemctl enable --now  linstor-satellite
sudo systemctl start linstor-satellite

# Create Volume
sudo fdisk /dev/sdb
sudo pvcreate /dev/sdb1
sudo vgcreate vg_drbd /dev/sdb1
sudo linstor storage-pool create lvm `hostname` pool_drbd vg_drbd

# Display Storage Pool
$ linstor storage-pool list
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
┊ StoragePool          ┊ Node   ┊ Driver   ┊ PoolName ┊ FreeCapacity ┊ TotalCapacity ┊ CanSnapshots ┊ State ┊
╞═══════════════════════════════════════════════════════════════════════════════════════════════════════════╡
┊ DfltDisklessStorPool ┊ base-j ┊ DISKLESS ┊          ┊              ┊               ┊ False        ┊ Ok    ┊
┊ DfltDisklessStorPool ┊ base-m ┊ DISKLESS ┊          ┊              ┊               ┊ False        ┊ Ok    ┊
┊ pool_drbd            ┊ base-j ┊ LVM      ┊ vg_drbd  ┊    10.00 GiB ┊     10.00 GiB ┊ False        ┊ Ok    ┊
┊ pool_drbd            ┊ base-m ┊ LVM      ┊ vg_drbd  ┊    10.00 GiB ┊     10.00 GiB ┊ False        ┊ Ok    ┊
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────╯

# Create resource-group
linstor resource-group create my_ssd_group --storage-pool pool_drbd --place-count 2

# Enable verify algorithm
linstor resource-group drbd-options --verify-alg crc32c my_ssd_group

# Create resource/volume
linstor resource-definition create share_store
linstor volume-definition create share_store 9500MB

# Placement
linstor resource create `hostname` share_store --storage-pool pool_drbd

# Waiting for sync
$ linstor resource list
╭────────────────────────────────────────────────────────────────────╮
┊ ResourceName ┊ Node   ┊ Port ┊ Usage  ┊ Conns ┊              State ┊
╞════════════════════════════════════════════════════════════════════╡
┊ share_store  ┊ base-j ┊ 7020 ┊ Unused ┊ Ok    ┊           UpToDate ┊
┊ share_store  ┊ base-m ┊ 7020 ┊ Unused ┊ Ok    ┊ SyncTarget(39.21%) ┊
╰────────────────────────────────────────────────────────────────────╯

# Finished
$ linstor resource list
╭──────────────────────────────────────────────────────────╮
┊ ResourceName ┊ Node   ┊ Port ┊ Usage  ┊ Conns ┊    State ┊
╞══════════════════════════════════════════════════════════╡
┊ share_store  ┊ base-j ┊ 7020 ┊ Unused ┊ Ok    ┊ UpToDate ┊
┊ share_store  ┊ base-m ┊ 7020 ┊ Unused ┊ Ok    ┊ UpToDate ┊
╰──────────────────────────────────────────────────────────╯

# Edit conf
$ vim /var/lib/linstor.d/share_store.re
net
{
    cram-hmac-alg     sha1;
    shared-secret     "XXXXXXXXX";

    # ADD THIS
    allow-two-primaries yes;
}

# Adjust
drbdadm adjust share_store

# Check mount
$ mount | grep drbd
/dev/drbd1012 on /drbd type ext4 (rw,relatime,data=ordered)
```

## [2] Install kea/stns/powerdns

```
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt

### Check
ansible-playbook -i hosts ./tasks/dnsdist.yaml -v --ask-pass --check

### Deploy
ansible-playbook -i hosts ./tasks/dnsdist.yaml -v --ask-pass

export SLACK_TOKEN=https://xxx
ansible-playbook -i hosts ./tasks/kea-hook-runscript.yaml -v --ask-pass
```
