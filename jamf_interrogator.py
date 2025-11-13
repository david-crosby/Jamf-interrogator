#!/usr/bin/env python3
"""
jamf interrogator - a practical cli tool for poking around your jamf environment
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
import csv
import logging

from jamfpy import Tenant


class JamfInterrogator:
    
    def __init__(self, config_path: Optional[Path] = None, log_level: int = logging.WARNING):
        self.logger = self._setup_logging(log_level)
        self.config = self._load_config(config_path)
        self.tenant = self._init_tenant()
    
    def _setup_logging(self, log_level: int) -> logging.Logger:
        logger = logging.getLogger('jamf_interrogator')
        logger.setLevel(log_level)
        
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(log_level)
        
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', 
                                     datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
        return logger
    
    def _load_config(self, config_path: Optional[Path]) -> dict:
        if config_path and config_path.exists():
            self.logger.debug(f"loading config from {config_path}")
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.logger.info(f"loaded config for {config.get('fqdn', 'unknown')}")
            return config
        
        self.logger.error("no config found - you'll need to provide credentials")
        print("no config found - you'll need to provide credentials")
        return {}
    
    def _init_tenant(self) -> Tenant:
        try:
            self.logger.info("connecting to jamf...")
            
            jamf_log_level = max(self.logger.level, logging.WARNING)
            
            tenant = Tenant(
                fqdn=self.config.get('fqdn'),
                auth_method=self.config.get('auth_method', 'oauth2'),
                client_id=self.config.get('client_id'),
                client_secret=self.config.get('client_secret'),
                username=self.config.get('username'),
                password=self.config.get('password'),
                log_level=jamf_log_level,
                safe_mode=True
            )
            
            self.logger.info("connected successfully")
            return tenant
            
        except Exception as e:
            self.logger.critical(f"connection failed: {e}")
            print(f"couldn't connect to jamf: {e}")
            sys.exit(1)
    
    def list_policies(self, output_format: str = 'table'):
        self.logger.info("fetching policies")
        
        response = self.tenant.classic.policies.get_all()
        
        if not response.ok:
            self.logger.error(f"api returned {response.status_code}")
            print(f"failed to fetch policies: {response.status_code}")
            return
        
        data = response.json()
        policies = data.get('policies', [])
        self.logger.debug(f"received {len(policies)} policies")
        
        if output_format == 'json':
            print(json.dumps(policies, indent=2))
        elif output_format == 'csv':
            self._output_csv(policies, ['id', 'name'])
        else:
            print(f"\nfound {len(policies)} policies:")
            print(f"{'ID':<8} {'Name':<50}")
            print("-" * 60)
            for policy in policies:
                print(f"{policy['id']:<8} {policy['name']:<50}")
    
    def list_computers(self, output_format: str = 'table'):
        self.logger.info("fetching computers")
        
        response = self.tenant.classic.computers.get_all()
        
        if not response.ok:
            self.logger.error(f"api returned {response.status_code}")
            print(f"failed to fetch computers: {response.status_code}")
            return
        
        data = response.json()
        computers = data.get('computers', [])
        self.logger.debug(f"received {len(computers)} computers")
        
        if output_format == 'json':
            print(json.dumps(computers, indent=2))
        elif output_format == 'csv':
            self._output_csv(computers, ['id', 'name', 'serial_number'])
        else:
            print(f"\nfound {len(computers)} computers:")
            print(f"{'ID':<8} {'Name':<40} {'Serial':<15}")
            print("-" * 65)
            for comp in computers:
                serial = comp.get('serial_number', 'N/A')
                print(f"{comp['id']:<8} {comp['name']:<40} {serial:<15}")
    
    def search_by_name(self, query: str, endpoint: str):
        self.logger.info(f"searching {endpoint} for '{query}'")
        
        endpoint_map = {
            'policies': self.tenant.classic.policies,
            'computers': self.tenant.classic.computers,
            'scripts': self.tenant.classic.scripts,
            'packages': self.tenant.classic.packages,
            'groups': self.tenant.classic.computer_groups
        }
        
        if endpoint not in endpoint_map:
            self.logger.error(f"unknown endpoint: {endpoint}")
            print(f"unknown endpoint: {endpoint}")
            print(f"available: {', '.join(endpoint_map.keys())}")
            return
        
        ep = endpoint_map[endpoint]
        response = ep.get_all()
        
        if not response.ok:
            self.logger.error(f"api returned {response.status_code}")
            print(f"failed to fetch data: {response.status_code}")
            return
        
        data = response.json()
        items = data.get(endpoint, [])
        self.logger.debug(f"searching through {len(items)} items")
        
        matches = [item for item in items if query.lower() in item.get('name', '').lower()]
        
        self.logger.info(f"found {len(matches)} matches")
        print(f"\nfound {len(matches)} matches:")
        for item in matches:
            print(f"  [{item['id']}] {item['name']}")
    
    def get_details(self, endpoint: str, item_id: int, save_to: Optional[Path] = None):
        self.logger.info(f"fetching {endpoint} id {item_id}")
        
        endpoint_map = {
            'policy': self.tenant.classic.policies,
            'computer': self.tenant.classic.computers,
            'script': self.tenant.classic.scripts,
            'package': self.tenant.classic.packages,
            'group': self.tenant.classic.computer_groups
        }
        
        if endpoint not in endpoint_map:
            self.logger.error(f"unknown endpoint: {endpoint}")
            print(f"unknown endpoint: {endpoint}")
            return
        
        ep = endpoint_map[endpoint]
        response = ep.get_by_id(item_id)
        
        if not response.ok:
            self.logger.error(f"api returned {response.status_code}")
            print(f"failed to fetch details: {response.status_code}")
            return
        
        data = response.json()
        
        if save_to:
            self.logger.debug(f"saving to {save_to}")
            with open(save_to, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"saved to {save_to}")
        else:
            print(json.dumps(data, indent=2))
    
    def list_scripts(self, output_format: str = 'table'):
        self.logger.info("fetching scripts")
        
        response = self.tenant.classic.scripts.get_all()
        
        if not response.ok:
            self.logger.error(f"api returned {response.status_code}")
            print(f"failed to fetch scripts: {response.status_code}")
            return
        
        data = response.json()
        scripts = data.get('scripts', [])
        self.logger.debug(f"received {len(scripts)} scripts")
        
        if output_format == 'json':
            print(json.dumps(scripts, indent=2))
        elif output_format == 'csv':
            self._output_csv(scripts, ['id', 'name'])
        else:
            print(f"\nfound {len(scripts)} scripts:")
            print(f"{'ID':<8} {'Name':<50}")
            print("-" * 60)
            for script in scripts:
                print(f"{script['id']:<8} {script['name']:<50}")
    
    def compare_items(self, endpoint: str, id1: int, id2: int):
        self.logger.info(f"comparing {endpoint} {id1} vs {id2}")
        
        endpoint_map = {
            'policy': self.tenant.classic.policies,
            'script': self.tenant.classic.scripts,
            'group': self.tenant.classic.computer_groups
        }
        
        if endpoint not in endpoint_map:
            self.logger.error(f"unknown endpoint: {endpoint}")
            print(f"unknown endpoint: {endpoint}")
            return
        
        ep = endpoint_map[endpoint]
        
        self.logger.debug(f"fetching {endpoint} {id1}")
        resp1 = ep.get_by_id(id1)
        self.logger.debug(f"fetching {endpoint} {id2}")
        resp2 = ep.get_by_id(id2)
        
        if not resp1.ok or not resp2.ok:
            self.logger.error("failed to fetch one or both items")
            print("failed to fetch one or both items")
            return
        
        data1 = resp1.json()
        data2 = resp2.json()
        
        all_keys = set(data1.keys()) | set(data2.keys())
        differences = 0
        
        print("\nkey differences:")
        for key in sorted(all_keys):
            val1 = data1.get(key)
            val2 = data2.get(key)
            
            if val1 != val2:
                differences += 1
                print(f"\n{key}:")
                print(f"  [{id1}]: {val1}")
                print(f"  [{id2}]: {val2}")
        
        self.logger.info(f"found {differences} differences")
    
    def audit_empty_groups(self):
        self.logger.info("starting empty groups audit")
        
        response = self.tenant.classic.computer_groups.get_all()
        
        if not response.ok:
            self.logger.error(f"api returned {response.status_code}")
            print(f"failed to fetch groups: {response.status_code}")
            return
        
        data = response.json()
        groups = data.get('computer_groups', [])
        
        print(f"\nchecking {len(groups)} groups...")
        empty_groups = []
        
        for idx, group in enumerate(groups, 1):
            self.logger.debug(f"checking group {idx}/{len(groups)}: {group['name']}")
            
            detail_resp = self.tenant.classic.computer_groups.get_by_id(group['id'])
            if detail_resp.ok:
                detail = detail_resp.json()
                group_data = detail.get('computer_group', {})
                computers = group_data.get('computers', [])
                
                if len(computers) == 0:
                    empty_groups.append(group)
                    self.logger.debug(f"group {group['id']} is empty")
        
        self.logger.info(f"found {len(empty_groups)} empty groups")
        print(f"\nfound {len(empty_groups)} empty groups:")
        for group in empty_groups:
            print(f"  [{group['id']}] {group['name']}")
    
    def _output_csv(self, data: list, fields: list):
        if not data:
            self.logger.warning("no data to output")
            return
        
        self.logger.debug(f"outputting {len(data)} rows as csv")
        writer = csv.DictWriter(sys.stdout, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)


def create_sample_config():
    sample = {
        "fqdn": "https://your-tenant.jamfcloud.com",
        "auth_method": "oauth2",
        "client_id": "your_client_id_here",
        "client_secret": "your_client_secret_here"
    }
    
    config_path = Path.home() / '.jamf_interrogator.json'
    
    with open(config_path, 'w') as f:
        json.dump(sample, f, indent=2)
    
    print(f"created sample config at {config_path}")
    print("edit this file with your jamf credentials")


def main():
    parser = argparse.ArgumentParser(
        description='interrogate your jamf environment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  %(prog)s list policies
  %(prog)s list computers --format csv
  %(prog)s search scripts "cleanup"
  %(prog)s details policy 42
  %(prog)s compare policy 10 11
  %(prog)s audit empty-groups
        """
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        default=Path.home() / '.jamf_interrogator.json',
        help='path to config file'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        default='warning',
        help='set logging verbosity (default: warning)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='available commands')
    
    list_parser = subparsers.add_parser('list', help='list items')
    list_parser.add_argument('endpoint', choices=['policies', 'computers', 'scripts'])
    list_parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table')
    
    search_parser = subparsers.add_parser('search', help='search by name')
    search_parser.add_argument('endpoint', choices=['policies', 'computers', 'scripts', 'packages', 'groups'])
    search_parser.add_argument('query', help='search term')
    
    details_parser = subparsers.add_parser('details', help='get full details')
    details_parser.add_argument('endpoint', choices=['policy', 'computer', 'script', 'package', 'group'])
    details_parser.add_argument('id', type=int)
    details_parser.add_argument('--save', type=Path, help='save to file')
    
    compare_parser = subparsers.add_parser('compare', help='compare two items')
    compare_parser.add_argument('endpoint', choices=['policy', 'script', 'group'])
    compare_parser.add_argument('id1', type=int)
    compare_parser.add_argument('id2', type=int)
    
    audit_parser = subparsers.add_parser('audit', help='run audit checks')
    audit_parser.add_argument('check', choices=['empty-groups'])
    
    subparsers.add_parser('init', help='create sample config file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'init':
        create_sample_config()
        return
    
    log_level_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    interrogator = JamfInterrogator(args.config, log_level_map[args.log_level])
    
    if args.command == 'list':
        if args.endpoint == 'policies':
            interrogator.list_policies(args.format)
        elif args.endpoint == 'computers':
            interrogator.list_computers(args.format)
        elif args.endpoint == 'scripts':
            interrogator.list_scripts(args.format)
    
    elif args.command == 'search':
        interrogator.search_by_name(args.query, args.endpoint)
    
    elif args.command == 'details':
        interrogator.get_details(args.endpoint, args.id, args.save)
    
    elif args.command == 'compare':
        interrogator.compare_items(args.endpoint, args.id1, args.id2)
    
    elif args.command == 'audit':
        if args.check == 'empty-groups':
            interrogator.audit_empty_groups()


if __name__ == '__main__':
    main()
