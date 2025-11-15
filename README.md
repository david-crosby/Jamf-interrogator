# Jamf Interrogator

A cli tool for exploring and analysing your jamf environment. Built for quick queries and practical day-to-day operations.

This has been inspired by thejoeker12/jamfpy-python-sdk-jamfpro

THIS IS WIP, STILL A WORKING DRAFT!

NO WARRANTY, SHARED AS IS.

## What it does

- List policies, computers, scripts and other resources
- Search across endpoints by name
- Fetch detailed configuration for specific items
- Compare two items side-by-side
- Run audit checks (like finding empty groups)
- Export data in multiple formats (table, json, csv)
- Configurable logging for troubleshooting and debugging

## Installation

Using uv (recommended):

```zsh
uv pip install -e .
```

Or with standard pip:

```zsh
pip install -e .
```

Do yourself a favour and use UV

## setup

Create a config file with your jamf credentials:

```bash
python jamf_interrogator.py init
```

this creates `~/.jamf_interrogator.json` - edit it with your details:

```json
{
  "fqdn": "https://your-tenant.jamfcloud.com",
  "auth_method": "oauth2",
  "client_id": "your_client_id_here",
  "client_secret": "your_client_secret_here"
}
```

For basic auth, use:

```json
{
  "fqdn": "https://your-tenant.jamfcloud.com",
  "auth_method": "basic",
  "username": "your_username",
  "password": "your_password"
}
```

## usage

### logging

Control how much information the tool outputs:

```zsh
# quiet mode - only show errors and critical issues
python jamf_interrogator.py --log-level error list policies

# normal mode (default) - shows warnings
python jamf_interrogator.py list policies

# verbose mode - shows what's happening
python jamf_interrogator.py --log-level info list computers

# debug mode - shows everything including api calls
python jamf_interrogator.py --log-level debug search scripts cleanup
```

Logging output goes to stderr, so you can still redirect data:
```zsh
# logs to screen, csv data to file
python jamf_interrogator.py --log-level info list computers --format csv > computers.csv
```

Available log levels:
- `debug` - everything, useful for troubleshooting
- `info` - major operations and progress
- `warning` - potential issues (default)
- `error` - actual errors only
- `critical` - severe errors only

### List things

```zsh
# show all policies
python jamf_interrogator.py list policies

# export computers as csv
python jamf_interrogator.py list computers --format csv

# get scripts as json
python jamf_interrogator.py list scripts --format json
```

### Search

```zsh
# find policies containing "update"
python jamf_interrogator.py search policies update

# find scripts with "cleanup" in the name
python jamf_interrogator.py search scripts cleanup

# search packages
python jamf_interrogator.py search packages chrome
```

### Get details

```zsh
# view full policy configuration
python jamf_interrogator.py details policy 42

# save computer details to file
python jamf_interrogator.py details computer 123 --save computer_123.json

# inspect a script
python jamf_interrogator.py details script 7
```

### Compare items

```zsh
# compare two policies
python jamf_interrogator.py compare policy 10 11

# compare groups
python jamf_interrogator.py compare group 5 8
```

### Audit checks

```zsh
# find empty computer groups
python jamf_interrogator.py audit empty-groups
```

## Practical examples

**find all policies with a specific name pattern:**
```bash
python jamf_interrogator.py search policies "software update" 
```

**export all computers for spreadsheet analysis:**
```bash
python jamf_interrogator.py list computers --format csv > computers.csv
```

**grab policy config for backup:**
```bash
python jamf_interrogator.py details policy 42 --save policy_42_backup.json
```

**check for unused groups:**
```bash
python jamf_interrogator.py audit empty-groups
```

## Tips

- use `--format csv` to pipe output into spreadsheets or other tools
- save detailed configs with `--save` before making changes
- compare items to spot configuration drift between similar resources
- the tool respects the standard jamf api rate limits

## Extending

the code is structured to make adding new commands straightforward:

1. add your method to the `JamfInterrogator` class
2. wire it up in the `main()` function's argument parser
3. add the appropriate endpoint from the jamfpy sdk

## Troubleshooting

**"couldn't connect to jamf"**
- check your fqdn includes the full url (https://...)
- verify your credentials are correct
- ensure your api client has the right permissions

**"failed to fetch: 401"**
- your token might have expired - the tool will get a fresh one automatically
- check your client has read permissions for the endpoint

**"unknown endpoint"**
- make sure you're using the singular form for details/compare (policy not policies)
- check available endpoints in the help: `python jamf_interrogator.py --help`

## Requirements

- python 3.12+
- jamfpy (included in this repo)
- requests

## Author

David Crosby (Bing)
jamfpy (included in this repo) - Source thejoeker12/jamfpy-python-sdk-jamfpro

## Licence

Use it however you want - it's just a tool to make life easier
