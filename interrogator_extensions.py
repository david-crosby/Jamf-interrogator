#!/usr/bin/env python3
"""
example extensions for jamf_interrogator

this shows how you can add your own custom analysis tools on top of the interrogator.
copy the patterns here and modify to suit your needs.
"""

from jamf_interrogator import JamfInterrogator
from pathlib import Path
from datetime import datetime
import json


class CustomInterrogator(JamfInterrogator):
    
    def find_stale_policies(self, days: int = 90):
        self.logger.info(f"looking for policies not updated in {days} days")
        
        response = self.tenant.classic.policies.get_all()
        
        if not response.ok:
            self.logger.error(f"api returned {response.status_code}")
            print(f"failed to fetch policies: {response.status_code}")
            return
        
        data = response.json()
        policies = data.get('policies', [])
        
        print(f"\nchecking {len(policies)} policies...")
        
        for policy in policies[:5]:
            detail_resp = self.tenant.classic.policies.get_by_id(policy['id'])
            if detail_resp.ok:
                detail = detail_resp.json()
                print(f"  [{policy['id']}] {policy['name']}")
    
    def export_security_settings(self, output_dir: Path):
        self.logger.info("exporting security settings")
        
        output_dir.mkdir(exist_ok=True)
        
        profiles_resp = self.tenant.classic.configuration_profiles.get_all()
        if profiles_resp.ok:
            profiles_data = profiles_resp.json()
            profiles_file = output_dir / f"config_profiles_{datetime.now():%Y%m%d}.json"
            with open(profiles_file, 'w') as f:
                json.dump(profiles_data, f, indent=2)
            self.logger.info(f"saved profiles to {profiles_file}")
            print(f"saved profiles to {profiles_file}")
        
        restricted_resp = self.tenant.classic.restricted_software.get_all()
        if restricted_resp.ok:
            restricted_data = restricted_resp.json()
            restricted_file = output_dir / f"restricted_software_{datetime.now():%Y%m%d}.json"
            with open(restricted_file, 'w') as f:
                json.dump(restricted_data, f, indent=2)
            self.logger.info(f"saved restricted software to {restricted_file}")
            print(f"saved restricted software to {restricted_file}")
    
    def check_policy_scope_overlap(self):
        self.logger.info("checking for scope overlaps")
        
        response = self.tenant.classic.policies.get_all()
        
        if not response.ok:
            print("couldn't fetch policies")
            return
        
        data = response.json()
        policies = data.get('policies', [])
        
        policy_scopes = {}
        
        for policy in policies[:10]:
            detail_resp = self.tenant.classic.policies.get_by_id(policy['id'])
            if detail_resp.ok:
                detail = detail_resp.json()
                scope = detail.get('policy', {}).get('scope', {})
                policy_scopes[policy['id']] = {
                    'name': policy['name'],
                    'scope': scope
                }
        
        print(f"\nanalysed {len(policy_scopes)} policies")
        self.logger.info(f"analysed {len(policy_scopes)} policies for scope overlap")
    
    def generate_inventory_report(self, output_file: Path):
        self.logger.info("generating inventory report")
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'details': {}
        }
        
        computers_resp = self.tenant.classic.computers.get_all()
        if computers_resp.ok:
            computers = computers_resp.json().get('computers', [])
            report['summary']['total_computers'] = len(computers)
            report['details']['computers'] = computers
            self.logger.debug(f"added {len(computers)} computers to report")
        
        policies_resp = self.tenant.classic.policies.get_all()
        if policies_resp.ok:
            policies = policies_resp.json().get('policies', [])
            report['summary']['total_policies'] = len(policies)
            report['details']['policies'] = policies
            self.logger.debug(f"added {len(policies)} policies to report")
        
        scripts_resp = self.tenant.classic.scripts.get_all()
        if scripts_resp.ok:
            scripts = scripts_resp.json().get('scripts', [])
            report['summary']['total_scripts'] = len(scripts)
            report['details']['scripts'] = scripts
            self.logger.debug(f"added {len(scripts)} scripts to report")
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"report saved to {output_file}")
        print(f"\nreport saved to {output_file}")
        print(f"  computers: {report['summary'].get('total_computers', 0)}")
        print(f"  policies: {report['summary'].get('total_policies', 0)}")
        print(f"  scripts: {report['summary'].get('total_scripts', 0)}")


def example_usage():
    config_path = Path.home() / '.jamf_interrogator.json'
    interrogator = CustomInterrogator(config_path)
    
    print("=== running custom analysis ===\n")
    
    interrogator.find_stale_policies(days=90)
    
    print("\n" + "="*50 + "\n")
    
    output_dir = Path.home() / 'jamf_exports'
    interrogator.export_security_settings(output_dir)
    
    print("\n" + "="*50 + "\n")
    
    interrogator.check_policy_scope_overlap()
    
    print("\n" + "="*50 + "\n")
    
    report_file = Path.home() / 'jamf_inventory_report.json'
    interrogator.generate_inventory_report(report_file)


if __name__ == '__main__':
    print("this is an example extension file")
    print("copy the methods you want into jamf_interrogator.py")
    print("or create your own custom interrogator class")
    print("\nto use: uncomment the example_usage() call below")
    
    # example_usage()
