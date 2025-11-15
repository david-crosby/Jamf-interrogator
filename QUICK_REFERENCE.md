# Jamf Interrogator - Very quick reference

Common tasks and one-liners for everyday use.

## Logging

```bash
# quiet operation - errors only
python jamf_interrogator.py --log-level error list policies

# see what's happening
python jamf_interrogator.py --log-level info list computers

# full debugging output
python jamf_interrogator.py --log-level debug search scripts backup
```

## Daily checks

```bash
# morning check - what's in the environment
python jamf_interrogator.py list policies | head -20
python jamf_interrogator.py list computers | wc -l

# find that policy you were working on yesterday
python jamf_interrogator.py search policies "software update"
```

## Before making changes

```bash
# backup current config
python jamf_interrogator.py details policy 42 --save backups/policy_42_before.json

# compare with production
python jamf_interrogator.py compare policy 42 43
```

## Troubleshooting

```bash
# find computers that haven't checked in
python jamf_interrogator.py list computers --format json | \
  jq '.[] | select(.last_contact_time < "2024-01-01")'

# locate all policies using a specific script
python jamf_interrogator.py list policies --format json | \
  jq '.[] | select(.scripts[].id == 7)'
```

## Reporting

```bash
# export everything for analysis
python jamf_interrogator.py list policies --format csv > reports/policies.csv
python jamf_interrogator.py list computers --format csv > reports/computers.csv
python jamf_interrogator.py list scripts --format csv > reports/scripts.csv

# combine into a quick summary
wc -l reports/*.csv
```

## Cleanup tasks

```bash
# find empty groups to potentially remove
python jamf_interrogator.py audit empty-groups > empty_groups.txt

# review and decide which to delete
cat empty_groups.txt
```

## Using with other tools

### With jq for json filtering

```bash
# get just policy names and ids
python jamf_interrogator.py list policies --format json | \
  jq '.[] | {id, name}'

# find policies with specific scope
python jamf_interrogator.py details policy 42 | \
  jq '.policy.scope'
```

### With grep for quick searches

```bash
# find all adobe-related items
python jamf_interrogator.py list policies | grep -i adobe
python jamf_interrogator.py list packages | grep -i adobe
```

### With spreadsheets

```bash
# export to csv and open in numbers
python jamf_interrogator.py list computers --format csv > computers.csv
open -a Numbers computers.csv
```

## Scripting patterns

### Sackup all policies

```bash
#!/bin/zsh
# backup_policies.sh

mkdir -p backups/policies
for id in $(python jamf_interrogator.py list policies --format json | jq '.[].id'); do
  python jamf_interrogator.py details policy $id --save "backups/policies/policy_${id}.json"
done
```

### Weekly report

```bash
#!/bin/zsh
# weekly_report.sh

REPORT_DIR="reports/$(date +%Y%m%d)"
mkdir -p "$REPORT_DIR"

python jamf_interrogator.py list policies --format csv > "$REPORT_DIR/policies.csv"
python jamf_interrogator.py list computers --format csv > "$REPORT_DIR/computers.csv"
python jamf_interrogator.py audit empty-groups > "$REPORT_DIR/empty_groups.txt"

echo "report saved to $REPORT_DIR"
```

### find policies by package

```bash
#!/bin/zsh
# find_policies_using_package.sh

PACKAGE_NAME="$1"

if [ -z "$PACKAGE_NAME" ]; then
    echo "usage: $0 <package_name>"
    exit 1
fi

echo "searching for policies using package: $PACKAGE_NAME"

python jamf_interrogator.py list policies --format json | \
  jq --arg pkg "$PACKAGE_NAME" '.[] | select(.packages[]?.name == $pkg) | {id, name}'
```

## API limits and performance

- the jamf api has rate limits - be mindful when running bulk operations
- for large exports, csv format is faster than json
- use --save when fetching details to avoid re-querying
- consider caching results for repeated analysis

## Error handling

```bash
# check if command succeeded
if python jamf_interrogator.py list policies > /dev/null 2>&1; then
    echo "connection ok"
else
    echo "connection failed - check credentials"
fi

# retry with timeout
timeout 30s python jamf_interrogator.py list computers
```

## Keyboard shortcuts for terminal

when viewing long lists in terminal:

- `space` - page down
- `b` - page up  
- `/search_term` - search forward
- `q` - quit

pipe to less for better navigation:
```bash
python jamf_interrogator.py list policies | less
```
