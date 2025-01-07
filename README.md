# Sing-Box CLI

🎤 Cross-platform sing-box service manager.

![](assets/image.png)

## Install

### uv

Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### sing-box

Windows

```powershell
uv tool install sing-box-cli
```

Linux

```bash
uv tool install sing-box-cli
sudo ln -sf $(which sing-box-cli) /usr/local/bin/
```

## Run

Windows in Admin powershell

```powershell
sing-box-cli --help
```

Linux

```bash
sudo sing-box-cli --help
```
