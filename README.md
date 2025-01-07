# Sing-Box CLI

cross-platform sing-box service manager

![](assets/image.png)

## Install

### uv

windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

linux

```bash
# root
sudo su
# install as root
curl -LsSf https://astral.sh/uv/install.sh | sh
# create link
ln -s $(which uv) /usr/local/bin/uv
```

### sing-box

```bash
uv tool install sing-box-cli
```

## Run

Windows in Admin powershell

```powershell
sing-box-cli --help
```

Linux

```bash
sudo uv tool run sing-box-cli --help
```
