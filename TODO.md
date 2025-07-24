# TODO.md - Multi-cloud Roadmap

This document presents the analysis and recommendations for extending the `cloud-securitygroup-grapher` role to other cloud providers.

## Current Status

✅ **Implemented**:
- **OpenStack** : Complete support with `openstack.cloud` collection
- **AWS** : Complete support with `amazon.aws` collection
- **Unified architecture** : Data normalization, shared templates
- **Multi-formats** : DOT/CSV/Markdown generation for all providers

## Cloud Provider Analysis

### 🔴 GCP (Google Cloud Platform) - **NOT RECOMMENDED**

**Issues identified**:
- **Conceptual incompatibility** : GCP uses network-level Firewall Rules, not Security Groups
- **Different paradigm** : Tag-based targeting vs instance attachment
- **High complexity** : Requires forced and artificial abstraction
- **Low ROI** : High development effort for poor results

**GCP Architecture**:
```yaml
# GCP Firewall (incompatible)
firewall_rule:
  name: "allow-http"
  direction: "INGRESS"
  targetTags: ["web-servers"]  # Tags on instances
  allowed: [{IPProtocol: "tcp", ports: ["80"]}]

# vs Security Groups (OpenStack/AWS)
security_group:
  rules: [...]
  attached_instances: [...]
```

**Conclusion** : ❌ **Abandon GCP support** - Fundamental architectural incompatibility

---

### ✅ Azure - **STRONGLY RECOMMENDED**

**Advantages**:
- **Perfect compatibility** : Azure Network Security Groups ≈ OpenStack Security Groups
- **Simple integration** : Direct normalization without abstraction
- **High ROI** : Maximum reuse of existing architecture
- **Consistent experience** : Identical user interface

**Azure Architecture (compatible)**:
```yaml
# Azure NSG (compatible)
network_security_group:
  name: "web-nsg"
  security_rules:
    - direction: "Inbound"
      protocol: "Tcp"
      destination_port_range: "80"
      source_address_prefix: "*"
```

**Ansible Collections**:
- `azure.azcollection`
- Modules : `azure_rm_securitygroup_info`, `azure_rm_virtualmachine_info`

## Azure Implementation Plan

### Phase 1 : Basic Azure Support (2-3 days)

#### Files to create/modify :

1. **`defaults/main.yml`** - New Azure variables :
```yaml
# Azure configuration
osggrapherAzureSubscriptionId: ""      # Azure Subscription (mandatory)
osggrapherAzureResourceGroup: ""       # Resource Group (mandatory)
osggrapherAzureRegion: ""              # Region (ex: westeurope)
osggrapherAzureTenantId: ""            # Azure AD Tenant
osggrapherAzureClientId: ""            # Service Principal ID
osggrapherAzureSecret: ""              # Service Principal Secret
```

2. **`requirements.yml`** - Add Azure collection :
```yaml
collections:
  - name: openstack.cloud
    version: ">=2.0.0"
  - name: amazon.aws
    version: ">=6.0.0"
  - name: azure.azcollection
    version: ">=1.0.0"
```

3. **`tasks/collect_azure.yml`** - Azure data collection :
```yaml
- name: Get Azure Network Security Groups
  azure.azcollection.azure_rm_securitygroup_info:
    resource_group: "{{ osggrapherAzureResourceGroup }}"
    subscription_id: "{{ osggrapherAzureSubscriptionId }}"
  register: azure_raw_nsgs

- name: Get Azure Virtual Machines
  azure.azcollection.azure_rm_virtualmachine_info:
    resource_group: "{{ osggrapherAzureResourceGroup }}"
  register: azure_raw_vms
  when: osggrapherShowInstances
```

4. **`tasks/normalize_azure.yml`** - Data normalization :
```yaml
- name: Normalize Azure security groups
  set_fact:
    normalized_sgs: "{{ azure_raw_nsgs.securitygroups | map('normalize_azure_sg') | list }}"

- name: Normalize Azure instances
  set_fact:
    normalized_instances: "{{ azure_raw_vms.vms | map('normalize_azure_instance') | list }}"
  when: osggrapherShowInstances
```

5. **`filter_plugins/cloud_normalizers.py`** - New Azure filter :
```python
def normalize_azure_sg(self, azure_nsg):
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
                
                if rule.get('action') == 'Allow':
                    normalized_rules.append(normalized_rule)
    
    return {
        'id': azure_nsg.get('name'),
        'name': azure_nsg.get('name'),
        'description': azure_nsg.get('tags', {}).get('description', ''),
        'rules': sorted(normalized_rules, key=lambda x: x.get('priority', 1000)),
        'provider': 'azure'
    }
```

6. **`tasks/main.yml`** - Azure provider validation :
```yaml
- name: Validate cloud provider
  assert:
    that: osggrapherCloudProvider in ['openstack', 'aws', 'azure']
    msg: "Supported cloud providers: openstack, aws, azure. Current: {{ osggrapherCloudProvider }}"
```

### Phase 2 : Advanced Azure Features (1-2 days)

#### Azure-specific enhancements :

1. **Priority management** : Sort rules by Azure priority
2. **Service Tags** : Support predefined tags (`Internet`, `VirtualNetwork`)
3. **Deny rules** : Visualization of blocking rules (Azure-specific)
4. **Augmented rules** : Support multi-port/multi-source rules

#### Azure-specific templates :
```jinja2
{% if cloud_provider == "azure" %}
  {# Azure priority display #}
  <tr><td><i>Priority: {{ rule.priority }}</i></td></tr>
  
  {# Deny rules in red #}
  {% if rule.action == "Deny" %}
    [style=dashed,color=red,label="DENY: {{ protocol }} {{ port_range }}"]
  {% endif %}
{% endif %}
```

### Phase 3 : Testing and Documentation (1 day)

1. **Testing** :
   - Ansible syntax validation
   - Testing with Azure test environment
   - Graphics generation verification

2. **Documentation** :
   - Update `README.md` with Azure examples
   - Update `CLAUDE.md` with tri-cloud architecture
   - Azure playbook examples

## Final Usage Examples

### OpenStack (existing)
```yaml
- role: cloud-securitygroup-grapher
  osggrapherCloudProvider: openstack
  osggrapherCloudInfra: MyCloud
  osggrapherShowInstances: true
```

### AWS (current)
```yaml
- role: cloud-securitygroup-grapher
  osggrapherCloudProvider: aws
  osggrapherAwsRegion: eu-west-1
  osggrapherAwsProfile: production
  osggrapherFilter: "prod-"
```

### Azure (new)
```yaml
- role: cloud-securitygroup-grapher
  osggrapherCloudProvider: azure
  osggrapherAzureSubscriptionId: "12345678-1234-1234-1234-123456789012"
  osggrapherAzureResourceGroup: "prod-rg"
  osggrapherAzureRegion: "westeurope"
  osggrapherShowInstances: true
```

## Expected Benefits

### Cloud Coverage
- **Before** : OpenStack + AWS
- **After** : OpenStack + AWS + Azure
- **Coverage** : ~80% of enterprise cloud environments

### Architecture
- **Reuse** : 95% of existing code
- **Consistency** : Identical user interface
- **Maintainability** : Unified architecture preserved

### Development Effort
- **Estimation** : 4-6 days total
- **Risk** : Low (compatible concepts)
- **ROI** : High (minimal effort, significant added value)

## Conclusion

✅ **Recommendation** : Implement Azure support as priority

**Justification** :
1. **Perfect architectural compatibility** with existing concepts
2. **Minimal development effort** (4-6 days)
3. **Significant added value** (tri-cloud coverage)
4. **Maintains consistency** of user experience

**Next steps** :
1. Team approach validation
2. Azure test environment setup
3. Phase 1 implementation (basic support)
4. Testing and validation
5. Phase 2 implementation (advanced features)

---

*Document written following comparative analysis of cloud providers for cloud-securitygroup-grapher role extension*