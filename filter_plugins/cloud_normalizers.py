#!/usr/bin/env python3
"""
Ansible filter plugins for normalizing cloud provider security group data
"""

class FilterModule(object):
    """Filters for cloud security group normalization"""

    def filters(self):
        return {
            'normalize_openstack_sg': self.normalize_openstack_sg,
            'normalize_aws_sg': self.normalize_aws_sg,
            'normalize_openstack_instance': self.normalize_openstack_instance,
            'normalize_aws_instance': self.normalize_aws_instance
        }

    def normalize_openstack_sg(self, openstack_sg):
        """Normalize OpenStack security group to unified format"""
        normalized_rules = []
        
        for rule in openstack_sg.get('security_group_rules', []):
            normalized_rule = {
                'direction': rule.get('direction'),
                'protocol': rule.get('protocol') or 'any',
                'port_min': rule.get('port_range_min'),
                'port_max': rule.get('port_range_max'),
                'remote_ip': rule.get('remote_ip_prefix'),
                'remote_sg_id': rule.get('remote_group_id'),
                'ethertype': rule.get('ethertype', 'IPv4')
            }
            normalized_rules.append(normalized_rule)
        
        return {
            'id': openstack_sg.get('id'),
            'name': openstack_sg.get('name'),
            'description': openstack_sg.get('description', ''),
            'rules': normalized_rules,
            'provider': 'openstack'
        }

    def normalize_aws_sg(self, aws_sg):
        """Normalize AWS security group to unified format"""
        normalized_rules = []
        
        # Process ingress rules
        for rule in aws_sg.get('IpPermissions', []):
            for ip_range in rule.get('IpRanges', []):
                normalized_rule = {
                    'direction': 'ingress',
                    'protocol': rule.get('IpProtocol', 'any'),
                    'port_min': rule.get('FromPort'),
                    'port_max': rule.get('ToPort'),
                    'remote_ip': ip_range.get('CidrIp'),
                    'remote_sg_id': None,
                    'ethertype': 'IPv4'
                }
                normalized_rules.append(normalized_rule)
            
            # Handle security group references
            for sg_ref in rule.get('UserIdGroupPairs', []):
                normalized_rule = {
                    'direction': 'ingress',
                    'protocol': rule.get('IpProtocol', 'any'),
                    'port_min': rule.get('FromPort'),
                    'port_max': rule.get('ToPort'),
                    'remote_ip': None,
                    'remote_sg_id': sg_ref.get('GroupId'),
                    'ethertype': 'IPv4'
                }
                normalized_rules.append(normalized_rule)
        
        # Process egress rules
        for rule in aws_sg.get('IpPermissionsEgress', []):
            for ip_range in rule.get('IpRanges', []):
                normalized_rule = {
                    'direction': 'egress',
                    'protocol': rule.get('IpProtocol', 'any'),
                    'port_min': rule.get('FromPort'),
                    'port_max': rule.get('ToPort'),
                    'remote_ip': ip_range.get('CidrIp'),
                    'remote_sg_id': None,
                    'ethertype': 'IPv4'
                }
                normalized_rules.append(normalized_rule)
            
            # Handle security group references
            for sg_ref in rule.get('UserIdGroupPairs', []):
                normalized_rule = {
                    'direction': 'egress',
                    'protocol': rule.get('IpProtocol', 'any'),
                    'port_min': rule.get('FromPort'),
                    'port_max': rule.get('ToPort'),
                    'remote_ip': None,
                    'remote_sg_id': sg_ref.get('GroupId'),
                    'ethertype': 'IPv4'
                }
                normalized_rules.append(normalized_rule)
        
        return {
            'id': aws_sg.get('GroupId'),
            'name': aws_sg.get('GroupName'),
            'description': aws_sg.get('Description', ''),
            'rules': normalized_rules,
            'provider': 'aws'
        }

    def normalize_openstack_instance(self, openstack_instance):
        """Normalize OpenStack instance to unified format"""
        return {
            'id': openstack_instance.get('id'),
            'name': openstack_instance.get('name'),
            'security_groups': [sg.get('name') for sg in openstack_instance.get('security_groups', [])],
            'provider': 'openstack'
        }

    def normalize_aws_instance(self, aws_instance):
        """Normalize AWS instance to unified format"""
        # Get Name from tags
        instance_name = aws_instance.get('InstanceId')
        for tag in aws_instance.get('Tags', []):
            if tag.get('Key') == 'Name':
                instance_name = tag.get('Value')
                break
        
        return {
            'id': aws_instance.get('InstanceId'),
            'name': instance_name,
            'security_groups': [sg.get('GroupId') for sg in aws_instance.get('SecurityGroups', [])],
            'provider': 'aws'
        }