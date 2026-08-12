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
            'normalize_aws_instance': self.normalize_aws_instance,
            'normalize_aws_interface': self.normalize_aws_interface,
            'azure_nsg_normalizer': self.azure_nsg_normalizer,
            'azure_vm_normalizer': self.azure_vm_normalizer,
            'azure_nic_normalizer': self.azure_nic_normalizer
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
        for rule in aws_sg.get('ip_permissions') or aws_sg.get('IpPermissions') or []:
            for ip_range in rule.get('ip_ranges') or rule.get('IpRanges') or []:
                normalized_rule = {
                    'direction': 'ingress',
                    'protocol': rule.get('ip_protocol') or rule.get('IpProtocol', 'any'),
                    'port_min': rule.get('from_port') or rule.get('FromPort'),
                    'port_max': rule.get('to_port') or rule.get('ToPort'),
                    'remote_ip': ip_range.get('cidr_ip') or ip_range.get('CidrIp'),
                    'remote_sg_id': None,
                    'ethertype': 'IPv4'
                }
                normalized_rules.append(normalized_rule)

            # Handle security group references
            for sg_ref in rule.get('user_id_group_pairs') or rule.get('UserIdGroupPairs') or []:
                normalized_rule = {
                    'direction': 'ingress',
                    'protocol': rule.get('ip_protocol') or rule.get('IpProtocol', 'any'),
                    'port_min': rule.get('from_port') or rule.get('FromPort'),
                    'port_max': rule.get('to_port') or rule.get('ToPort'),
                    'remote_ip': None,
                    'remote_sg_id': sg_ref.get('group_id') or sg_ref.get('GroupId'),
                    'ethertype': 'IPv4'
                }
                normalized_rules.append(normalized_rule)
        
        # Process egress rules
        for rule in aws_sg.get('ip_permissions_egress') or aws_sg.get('IpPermissionsEgress') or []:
            for ip_range in rule.get('ip_ranges') or rule.get('IpRanges') or []:
                normalized_rule = {
                    'direction': 'egress',
                    'protocol': rule.get('ip_protocol') or rule.get('IpProtocol', 'any'),
                    'port_min': rule.get('from_port') or rule.get('FromPort'),
                    'port_max': rule.get('to_port') or rule.get('ToPort'),
                    'remote_ip': ip_range.get('cidr_ip') or ip_range.get('CidrIp'),
                    'remote_sg_id': None,
                    'ethertype': 'IPv4'
                }
                normalized_rules.append(normalized_rule)

            # Handle security group references
            for sg_ref in rule.get('user_id_group_pairs') or rule.get('UserIdGroupPairs') or []:
                normalized_rule = {
                    'direction': 'egress',
                    'protocol': rule.get('ip_protocol') or rule.get('IpProtocol', 'any'),
                    'port_min': rule.get('from_port') or rule.get('FromPort'),
                    'port_max': rule.get('to_port') or rule.get('ToPort'),
                    'remote_ip': None,
                    'remote_sg_id': sg_ref.get('group_id') or sg_ref.get('GroupId'),
                    'ethertype': 'IPv4'
                }
                normalized_rules.append(normalized_rule)
        
        return {
            'id': aws_sg.get('group_id') or aws_sg.get('GroupId'),
            'name': aws_sg.get('group_name') or aws_sg.get('GroupName'),
            'description': aws_sg.get('description') or aws_sg.get('Description', ''),
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
        instance_id = aws_instance.get('instance_id') or aws_instance.get('InstanceId')
        instance_name = instance_id

        # Tags can be dict or list depending on context
        tags = aws_instance.get('tags') or aws_instance.get('Tags', [])
        if isinstance(tags, dict):
            # tags is a dict like {'Name': 'value'}
            instance_name = tags.get('Name', instance_name)
        elif isinstance(tags, list):
            # tags is a list of dicts like [{'Key': 'Name', 'Value': 'value'}]
            for tag in tags:
                if isinstance(tag, dict):
                    key = tag.get('key') or tag.get('Key')
                    value = tag.get('value') or tag.get('Value')
                    if key == 'Name':
                        instance_name = value
                        break

        security_groups = aws_instance.get('security_groups') or aws_instance.get('SecurityGroups', [])
        sg_ids = []
        for sg in security_groups:
            if isinstance(sg, dict):
                sg_id = sg.get('group_id') or sg.get('GroupId')
                if sg_id:
                    sg_ids.append(sg_id)
            elif isinstance(sg, str):
                # Sometimes security_groups is just a list of IDs
                sg_ids.append(sg)

        return {
            'id': instance_id,
            'name': instance_name,
            'security_groups': sg_ids,
            'provider': 'aws'
        }

    def normalize_aws_interface(self, aws_interface):
        """Normalize AWS network interface to unified format"""
        interface_id = aws_interface.get('network_interface_id') or aws_interface.get('NetworkInterfaceId')

        # Get description or use ID as name
        interface_name = aws_interface.get('description') or aws_interface.get('Description') or interface_id

        # Get security groups
        groups = aws_interface.get('groups') or aws_interface.get('Groups', [])
        sg_ids = []
        for sg in groups:
            if isinstance(sg, dict):
                sg_id = sg.get('group_id') or sg.get('GroupId')
                if sg_id:
                    sg_ids.append(sg_id)
            elif isinstance(sg, str):
                sg_ids.append(sg)

        return {
            'id': interface_id,
            'name': interface_name,
            'security_groups': sg_ids,
            'provider': 'aws'
        }

    def azure_nsg_normalizer(self, azure_nsgs):
        """Normalize Azure NSGs list to unified format"""
        return [self.normalize_azure_nsg(nsg) for nsg in azure_nsgs]

    def normalize_azure_nsg(self, azure_nsg):
        """Normalize Azure NSG to unified format"""
        normalized_rules = []
        
        for rule in azure_nsg.get('security_rules', []):
            # Handle Azure multi-port and multi-source rules
            dest_ports = rule.get('destination_port_ranges', []) or [rule.get('destination_port_range', 'any')]
            source_prefixes = rule.get('source_address_prefixes', []) or [rule.get('source_address_prefix', '0.0.0.0/0')]
            
            for port in dest_ports:
                for source in source_prefixes:
                    port_min, port_max = self._parse_azure_port_range(port)
                    
                    normalized_rule = {
                        'direction': rule.get('direction', 'Inbound').lower().replace('inbound', 'ingress').replace('outbound', 'egress'),
                        'protocol': rule.get('protocol', 'any').lower(),
                        'port_min': port_min,
                        'port_max': port_max,
                        'remote_ip': self._normalize_azure_source(source),
                        'remote_sg_id': None,
                        'ethertype': 'IPv4',
                        'priority': rule.get('priority'),
                        'action': rule.get('action', 'Allow')
                    }
                    
                    # Only include Allow rules (skip Deny rules for visualization)
                    if rule.get('action') == 'Allow':
                        normalized_rules.append(normalized_rule)
        
        return {
            'id': azure_nsg.get('name'),
            'name': azure_nsg.get('name'),
            'description': azure_nsg.get('tags', {}).get('description', ''),
            'rules': sorted(normalized_rules, key=lambda x: x.get('priority', 1000)),
            'provider': 'azure'
        }

    def azure_vm_normalizer(self, azure_vms):
        """Normalize Azure VMs list to unified format"""
        return [self.normalize_azure_vm(vm) for vm in azure_vms]

    def normalize_azure_vm(self, azure_vm):
        """Normalize Azure VM to unified format"""
        # Extract security groups from network interfaces
        security_groups = []
        for nic in azure_vm.get('network_interfaces', []):
            if 'network_security_group' in nic:
                nsg_name = nic['network_security_group'].get('name')
                if nsg_name and nsg_name not in security_groups:
                    security_groups.append(nsg_name)
        
        return {
            'id': azure_vm.get('id'),
            'name': azure_vm.get('name'),
            'security_groups': security_groups,
            'provider': 'azure'
        }

    def azure_nic_normalizer(self, azure_nics):
        """Normalize Azure NICs list to unified format"""
        return [self.normalize_azure_nic(nic) for nic in azure_nics]

    def normalize_azure_nic(self, azure_nic):
        """Normalize Azure NIC to unified format"""
        # Get primary IP configuration
        fixed_ips = []
        for ip_config in azure_nic.get('ip_configurations', []):
            if ip_config.get('private_ip_address'):
                fixed_ips.append({
                    'ip_address': ip_config['private_ip_address']
                })
        
        # Extract security groups
        security_groups = []
        if azure_nic.get('network_security_group'):
            security_groups.append(azure_nic['network_security_group'].get('name'))
        
        return {
            'id': azure_nic.get('id'),
            'name': azure_nic.get('name', ''),
            'fixed_ips': fixed_ips,
            'security_groups': security_groups,
            'provider': 'azure'
        }

    def _parse_azure_port_range(self, port):
        """Parse Azure port range to min/max"""
        if not port or port == 'any' or port == '*':
            return None, None
        
        if '-' in str(port):
            parts = str(port).split('-')
            return int(parts[0]), int(parts[1])
        else:
            port_num = int(port)
            return port_num, port_num

    def _normalize_azure_source(self, source):
        """Normalize Azure source address"""
        if not source or source == '*':
            return '0.0.0.0/0'
        
        # Handle Azure service tags
        azure_service_tags = {
            'Internet': '0.0.0.0/0',
            'VirtualNetwork': '10.0.0.0/8',
            'AzureLoadBalancer': '168.63.129.16/32'
        }
        
        return azure_service_tags.get(source, source)