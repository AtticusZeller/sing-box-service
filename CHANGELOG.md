# Changelog

All notable changes to this project will be documented in this file.

## 0.0.56 - 2025-10-23

### ⚙️ Miscellaneous Tasks

- *(CI)* Update go version to stable
- Update sing-box binary to version v1.12.11

## 0.0.55 - 2025-10-15

### ⚙️ Miscellaneous Tasks

- Update sing-box binary to version v1.12.10

## 0.0.54 - 2025-10-06

### ⚙️ Miscellaneous Tasks

- *(github-actions)* Bump actions/checkout from 4 to 5 (#17) in #17
- Update sing-box binary to version v1.12.9

## 0.0.53 - 2025-09-14

### ⚙️ Miscellaneous Tasks

- Update sing-box binary to version v1.12.3
- Update sing-box binary to version v1.12.4
- Update sing-box binary to version v1.12.5
- Update sing-box binary to version v1.12.7
- *(github-actions)* Bump actions/setup-go from 5 to 6 (#18) in #18
- Update sing-box binary to version v1.12.8

## 0.0.52 - 2025-08-21

### ⚙️ Miscellaneous Tasks

- Update sing-box binary to version v1.12.2

## 0.0.51 - 2025-08-17

### ⚙️ Miscellaneous Tasks

- Update sing-box binary to version v1.12.1

## 0.0.50 - 2025-08-04

### ⚙️ Miscellaneous Tasks

- Update sing-box binary to version v1.12.0

## 0.0.49 - 2025-07-09

### ⚙️ Miscellaneous Tasks

- Pre-commit autoupdate (#15) in #15
- Update sing-box binary to version v1.11.15

## 0.0.48 - 2025-06-20

### ⚙️ Miscellaneous Tasks

- Update sing-box binary to version v1.11.14

## 0.0.47 - 2025-06-05

### 🚜 Refactor

- Remove redundant linux service io/cpu config

### ⚙️ Miscellaneous Tasks

- Update sing-box binary to version v1.11.13

## 0.0.46 - 2025-05-19

### 🐛 Bug Fixes

- Remove grey output

### ⚙️ Miscellaneous Tasks

- Update sing-box binary to version v1.11.11

## 0.0.45 - 2025-05-09

### 🐛 Bug Fixes

- Show diff wrong

### 🧪 Testing

- Add test for config.utils

### ⚙️ Miscellaneous Tasks

- Replace json load with pydantic api

## 0.0.44 - 2025-05-07

### 🐛 Bug Fixes

- Specify one config file and unify sing-box run cmd
- Add SERVICE_PAUSED into nssm service status list
- Py 3.11 is needed for `Self` typing annotation at least

### 🚜 Refactor

- Split config into sing-box config and app config

### ⚙️ Miscellaneous Tasks

- Rename SingBoxConfig as  ConfigHandler
- Remove redundant code
- Format in #14

## 0.0.43 - 2025-05-06

### 🚀 Features

- Add `--clear-cache` ,`-cc` option for `run`, `service restart`

### 🐛 Bug Fixes

- Avoid debug output

### 🚜 Refactor

- Rename `clean_cache` to `clear_cache`

### ⚙️ Miscellaneous Tasks

- *(github-actions)* Bump astral-sh/setup-uv from 5 to 6 (#12) in #12
- Update sing-box binary to version v1.11.10
- Format

## 0.0.42 - 2025-04-28

### ⚙️ Miscellaneous Tasks

- Update sing-box binary to version v1.11.9

## 0.0.41 - 2025-04-24

### 🚜 Refactor

- Replace ScheduledTask with nssm of window service in #11

## 0.0.40 - 2025-04-19

### ⚙️ Miscellaneous Tasks

- *(github-actions)* Bump actions/checkout from 2 to 4 (#10) in #10
- Update sing-box binary to version v1.11.8

## 0.0.39 - 2025-04-09

### 🐛 Bug Fixes

- Go build version in ci

### ⚙️ Miscellaneous Tasks

- Update sing-box binary to version v1.11.7

## 0.0.38 - 2025-04-09

### 🚀 Features

- Add fallback sing-box bins

### 🐛 Bug Fixes

- Run_cmd of service and early stop in run (#7) in #7
- No known parent package

### ⚙️ Miscellaneous Tasks

- Remove redundant stop process ps_cmd in #8
- Remove redundant if condition for Config.bin_path
- Remove lru_cache
- Update sing-box binary to version v1.11.7

## 0.0.37 - 2025-03-31

### 🚜 Refactor

- Simplify config class in #5
- Enable windows powershell as executor

### ⚙️ Miscellaneous Tasks

- Update test script
- Update pre-commit

## 0.0.36 - 2025-03-26

### 🐛 Bug Fixes

- Sing-box-beta bin_path

### 🧪 Testing

- Add pytest tools

### ⚙️ Miscellaneous Tasks

- Remove redundant `check_url()` in config.utils
- Rename load_json_config as load_json_asdict
- Order commands in `pre-commit.sh`

## 0.0.35 - 2025-03-26

### 🐛 Bug Fixes

- Elevate privilege for pwsh and delay the execution of task to user login on

## 0.0.34 - 2025-03-25

### 🐛 Bug Fixes

- Print friendly as `ensure_root()` failed

### 🚜 Refactor

- Create_service pwsh command

## 0.0.33 - 2025-03-25

### 🚜 Refactor

- Apply type cast for typer.Context

### ⚙️ Miscellaneous Tasks

- Simplify methods of config class
- Remove #TODO:
- Remove duplicate print
- Add test for windows

## 0.0.32 - 2025-03-25

### 🐛 Bug Fixes

- Clean_cache exception handle in windows
- `run` in windows

## 0.0.31 - 2025-03-23

### 🐛 Bug Fixes

- Typo

## 0.0.30 - 2025-03-23

### 🚀 Features

- Add `--token` option for config update

## 0.0.29 - 2025-03-22

### 🚀 Features

- Add update option for `run` and `service restart` to update config automatically
- Add `--restart` option for `config add-sub`

### 📚 Documentation

- Fix email

### ⚙️ Miscellaneous Tasks

- Rename dir sing_box_service as sing_box_cli
- Replace creating service  instance manually with context object

## 0.0.28 - 2025-03-21

### ⚙️ Miscellaneous Tasks

- Remove commands about capture logs in windows

## 0.0.27 - 2025-03-21

### 🐛 Bug Fixes

- Catch `asyncio.exceptions.CancelledError` while canceling stats display
- Logic of load groups, when to update delay and load delay history

### 🚜 Refactor

- Replace SingBoxCli class with typer context and modularize commands files
- Make_stream_request
- Display logs from api_client
- Simplify config_dir

### ⚙️ Miscellaneous Tasks

- Remove EmptyResponse
- Simplify api commands in top level

## 0.0.26 - 2025-03-20

### 🚜 Refactor

- Validate responses using pydantic

## 0.0.25 - 2025-03-20

### 🐛 Bug Fixes

- Set fixed interval to avoid repeated traffic data

## 0.0.24 - 2025-03-19

### 🚜 Refactor

- Smooth traffic data

## 0.0.23 - 2025-03-19

### 🚀 Features

- Replace connection table with traffic graph in stats command

### 📚 Documentation

- Update README.md command --help

## 0.0.22 - 2025-03-18

### 🐛 Bug Fixes

- Commands annotation

## 0.0.21 - 2025-03-18

### 🐛 Bug Fixes

- Replace None of host with destination ip

## 0.0.20 - 2025-03-18

### 🚀 Features

- Add stats command to visualize traffic, memory and connections
- Add cnns command to manage connections
- Add proxy command to select policy

### 🚜 Refactor

- Replace requests with httpx
- Check url using httpx

## 0.0.19 - 2025-03-15

### 🚀 Features

- Add simple run command

### ⚙️ Miscellaneous Tasks

- Add type annotationfor __init__

## 0.0.18 - 2025-03-15

### ⚙️ Miscellaneous Tasks

- Bump deps

## 0.0.17 - 2025-03-10

### 🐛 Bug Fixes

- Emoji alignment of logs

## 0.0.16 - 2025-03-10

### 🐛 Bug Fixes

- Start, restart logs

### 📚 Documentation

- Update --help image of README.md
- Remove example

## 0.0.15 - 2025-03-10

### 🚀 Features

- Add version command
- Show config file path while invoking command

### 🐛 Bug Fixes

- Remove service file while disable service
- Potential crash while init directory
- Redundant logs
- Logs info

### 🚜 Refactor

- Remove update command
- Config info

### 📚 Documentation

- Fix function docstring

## 0.0.14 - 2025-03-10

### 🐛 Bug Fixes

- Linux install dir using ~/.config

## 0.0.13 - 2025-03-08

### 🚀 Features

- Show diff after updating config

### 📚 Documentation

- Add sniff action
- Update cloudflare ip
- Client-server config
- Update config
- Update ntp server

### 🧪 Testing

- Add tests as scripts target

## 0.0.12 - 2025-02-28

### 🐛 Bug Fixes

- Pre-commit pretty json replace unicode emoji with ascii
- Increase hop interval
- Add RunOnlyIfNetworkAvailable
- Dashboard url

### ⚙️ Miscellaneous Tasks

- Update pre-commit and gitignore
- Add configs template
- Add server client config
- Update brutal limit
- Add microsoft rules
- Add rule

## 0.0.11 - 2025-01-20

### 🐛 Bug Fixes

- Add working dir, clean_cache command would work.

## 0.0.10 - 2025-01-15

### 🐛 Bug Fixes

- Systemd unit start condition in linux server and optimize the service priority

## 0.0.9 - 2025-01-14

### 🚀 Features

- Add config clean_cache

### 🐛 Bug Fixes

- Service start before network connection
- Linux service After start condition
- Remove tool synctime -w in  windows ,because newest sing-box has fixed ntp

### 📚 Documentation

- Update linux install and run

### ⚙️ Miscellaneous Tasks

- Update linux show logs prompt

## 0.0.5 - 2025-01-07

### 🚀 Features

- Enable windows logs

### 🐛 Bug Fixes

- Show and update config encode error
- Windows sys_platform
- Remove init_service
- Ignore mypy warn_unused_ignores
- Replace schtask with raw pwsh

### 📚 Documentation

- Update README.md

### ⚙️ Miscellaneous Tasks

- Type ignore
- Debug bin path

## 0.0.3 - 2025-01-07

### 🚀 Features

- Sing-box service,config,logs

### 🐛 Bug Fixes

- Cli name

<!-- generated by git-cliff -->
