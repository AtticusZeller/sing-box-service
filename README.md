# Sing-Box CLI

cross-platform sing-box service manager

![](assets/image.png)

## Install

### Init UV

```bash
# root
sudo su
# install as root
curl -LsSf https://astral.sh/uv/install.sh | sh
# create link
ln -s $(which uv) /usr/local/bin/uv
```

### Add sing-box

```bash
sudo uv tool install sing-box-cli
```

## Run

```bash
sudo uv tool run sing-box-cli --help
```
