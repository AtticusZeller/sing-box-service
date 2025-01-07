# Sing-Box CLI

cross-platform sing-box service manager

![](assets/image.png)

## Install

### init UV

```bash
# root
sudo su
# install as root
curl -LsSf https://astral.sh/uv/install.sh | sh
# create link
ln -s $(which uv) /usr/local/bin/uv
```

### add sing-box-service

```bash
sudo uv tool install sing-box-cli
```

## Run

```bash
sudo uvx sing-box --help
```
