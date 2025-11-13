#!/usr/bin/env python3
"""
programmatic usage examples

shows how to use the interrogator in your own python scripts
rather than through the cli interface
"""

from pathlib import Path
from jamf_interrogator import JamfInterrogator
import json
import logging


def example_basic_usage():
    config = Path.home() / '.jamf_interrogator.json'
    interrogator = JamfInterrogator(config)
    
    interrogator.list_policies(output_format='table')
    interrogator.list_policies(output_format='json')


def example_with_processing():
    config = Path.home() / '.jamf_interrogator.json'
    interrogator = JamfInterrogator(config)
    
    response = interrogator.tenant.classic.policies.get_all()
    
    if response.ok:
        data = response.json()
        policies = data.get('policies', [])
        
        for policy in policies:
            print(f"processing: {policy['name']}")
        
        print(f"\nprocessed {len(policies)} policies")


def example_batch_export():
    config = Path.home() / '.jamf_interrogator.json'
    interrogator = JamfInterrogator(config)
    
    export_dir = Path.home() / 'jamf_export'
    export_dir.mkdir(exist_ok=True)
    
    endpoints = [
        ('policies', interrogator.tenant.classic.policies),
        ('computers', interrogator.tenant.classic.computers),
        ('scripts', interrogator.tenant.classic.scripts),
        ('packages', interrogator.tenant.classic.packages),
    ]
    
    for name, endpoint in endpoints:
        print(f"exporting {name}...")
        response = endpoint.get_all()
        
        if response.ok:
            data = response.json()
            output_file = export_dir / f"{name}.json"
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"  saved to {output_file}")


def example_custom_analysis():
    config = Path.home() / '.jamf_interrogator.json'
    interrogator = JamfInterrogator(config)
    
    comp_response = interrogator.tenant.classic.computers.get_all()
    
    if not comp_response.ok:
        print("couldn't fetch computers")
        return
    
    computers = comp_response.json().get('computers', [])
    
    serial_prefixes = {}
    
    for computer in computers:
        serial = computer.get('serial_number', '')
        if serial:
            prefix = serial[:4]
            serial_prefixes[prefix] = serial_prefixes.get(prefix, 0) + 1
    
    print("\ncomputers by serial prefix:")
    for prefix, count in sorted(serial_prefixes.items()):
        print(f"  {prefix}: {count}")


def example_with_error_handling():
    try:
        config = Path.home() / '.jamf_interrogator.json'
        interrogator = JamfInterrogator(config)
        
        response = interrogator.tenant.classic.policies.get_all()
        
        if response.ok:
            data = response.json()
            print(f"fetched {len(data.get('policies', []))} policies")
        else:
            print(f"api returned error: {response.status_code}")
            print(f"response: {response.text}")
    
    except FileNotFoundError:
        print("config file not found")
        print("run: python jamf_interrogator.py init")
    
    except KeyError as e:
        print(f"missing required config key: {e}")
    
    except Exception as e:
        print(f"unexpected error: {e}")


def example_finding_specific_items():
    config = Path.home() / '.jamf_interrogator.json'
    interrogator = JamfInterrogator(config)
    
    keywords = ['cleanup', 'backup', 'update']
    
    response = interrogator.tenant.classic.scripts.get_all()
    
    if response.ok:
        scripts = response.json().get('scripts', [])
        
        for keyword in keywords:
            matches = [s for s in scripts if keyword.lower() in s['name'].lower()]
            print(f"\nscripts containing '{keyword}': {len(matches)}")
            for script in matches[:5]:
                print(f"  [{script['id']}] {script['name']}")


def example_scheduled_report():
    from datetime import datetime
    
    config = Path.home() / '.jamf_interrogator.json'
    interrogator = JamfInterrogator(config)
    
    report = {
        'generated': datetime.now().isoformat(),
        'summary': {}
    }
    
    endpoints = {
        'policies': interrogator.tenant.classic.policies,
        'computers': interrogator.tenant.classic.computers,
        'scripts': interrogator.tenant.classic.scripts,
    }
    
    for name, endpoint in endpoints.items():
        response = endpoint.get_all()
        if response.ok:
            data = response.json()
            count = len(data.get(name, []))
            report['summary'][name] = count
    
    report_file = Path.home() / f"jamf_report_{datetime.now():%Y%m%d}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"daily report saved to {report_file}")
    print(f"summary: {report['summary']}")


def example_with_debug_logging():
    config = Path.home() / '.jamf_interrogator.json'
    
    interrogator = JamfInterrogator(config, log_level=logging.DEBUG)
    
    interrogator.list_policies(output_format='table')


if __name__ == '__main__':
    print("programmatic usage examples")
    print("=" * 50)
    print()
    print("uncomment the examples you want to run:")
    print()
    
    # example_basic_usage()
    # example_with_processing()
    # example_batch_export()
    # example_custom_analysis()
    # example_with_error_handling()
    # example_finding_specific_items()
    # example_scheduled_report()
    # example_with_debug_logging()
    
    print("see the function definitions above for usage patterns")
