# jamf interrogator - quick start

get up and running in 2 minutes.

## install

```bash
./setup_interrogator.sh
```

## configure

edit `~/.jamf_interrogator.json`:
```json
{
  "fqdn": "https://your-tenant.jamfcloud.com",
  "auth_method": "oauth2",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret"
}
```

## test

```bash
python jamf_interrogator.py list policies
```

## common commands

```bash
# list things
python jamf_interrogator.py list policies
python jamf_interrogator.py list computers
python jamf_interrogator.py list scripts

# search
python jamf_interrogator.py search policies "software update"
python jamf_interrogator.py search scripts cleanup

# get details
python jamf_interrogator.py details policy 42
python jamf_interrogator.py details policy 42 --save backup.json

# compare
python jamf_interrogator.py compare policy 10 11

# audit
python jamf_interrogator.py audit empty-groups

# export as csv
python jamf_interrogator.py list computers --format csv > computers.csv
```

## logging

```bash
# quiet (errors only)
python jamf_interrogator.py --log-level error list policies

# verbose (show progress)
python jamf_interrogator.py --log-level info list computers

# debug (everything)
python jamf_interrogator.py --log-level debug search scripts test
```

## help

```bash
python jamf_interrogator.py --help
python jamf_interrogator.py list --help
```

that's it. you're ready to interrogate.
