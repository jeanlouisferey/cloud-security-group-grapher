# cloud-securitygroup-grapher

This Ansible role gets information from cloud providers (OpenStack, AWS, Azure) and generates a [graphical representation](doc/CloudGrapher.png) of security groups and instances through a dot file rendered by [Graphviz](https://graphviz.gitlab.io/)

## ⚠️ **ALPHA VERSION - NOT PRODUCTION READY**

**This role is in early development stage (ALPHA) and has NOT been tested in real environments.**

- 🔴 **ALL PROVIDERS**: No serious testing has been conducted yet
- 🔴 **OpenStack support**: Implemented but untested
- 🔴 **AWS support**: Implemented but untested  
- 🔴 **Azure support**: Recently implemented, completely untested
- ❌ **Production use**: STRONGLY DISCOURAGED - may cause unexpected behavior

**⚠️ USE AT YOUR OWN RISK:**
- This is an **ALPHA release** for development and testing purposes only
- **No guarantees** on functionality, stability, or data safety
- May contain bugs, incomplete features, or breaking changes
- Test thoroughly in isolated environments before any real-world usage
- Contributions, bug reports, and testing feedback are highly welcomed
- See `tests/` directory for theoretical test scenarios (not yet validated)

## Requirements

The below requirements are needed on the host that executes this module.

* Ansible >= 2.9
* [openstack.cloud](https://docs.ansible.com/ansible/latest/collections/openstack/cloud/index.html#plugins-in-openstack-cloud) collection (version >= 2.0.0) - for OpenStack support
* [amazon.aws](https://docs.ansible.com/ansible/latest/collections/amazon/aws/index.html) collection (version >= 6.0.0) - for AWS support
* [azure.azcollection](https://docs.ansible.com/ansible/latest/collections/azure/azcollection/index.html) collection (version >= 1.0.0) - for Azure support
* :warning: For **OpenStack**: [OpenStack-SDK](https://docs.openstack.org/openstacksdk/latest/user/) python library (version >= 1.0.0) needs to be installed
* :warning: For **AWS**: [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) and [botocore](https://botocore.amazonaws.com/v1/documentation/api/latest/index.html) python libraries need to be installed
* :warning: For **Azure**: [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) or Azure SDK for Python needs to be installed
* :warning: To render (i.e. to draw and obtain a graphic file), [Graphviz](https://graphviz.gitlab.io/) needs to be installed.

## Role Variables

### Cloud Provider Configuration

|Name|Type|Description|Default|
|----|----|-----------|-------|
|`osggrapherCloudProvider`|string|Cloud provider to use: `openstack`, `aws`, or `azure` (**mandatory**)|`openstack`|

### OpenStack Configuration

|Name|Type|Description|Default|
|----|----|-----------|-------|
|`osggrapherCloudInfra`|string|Name of cloud infrastructure (defined in [clouds.yml](https://docs.openstack.org/python-openstackclient/pike/configuration/index.html)) where your tenant is. (**mandatory when using OpenStack**)|`""`|

### AWS Configuration

|Name|Type|Description|Default|
|----|----|-----------|-------|
|`osggrapherAwsRegion`|string|AWS region to query (**mandatory when using AWS**)|`""`|
|`osggrapherAwsProfile`|string|AWS profile to use (defined in ~/.aws/credentials)|`default`|

### Azure Configuration

|Name|Type|Description|Default|
|----|----|-----------|-------|
|`osggrapherAzureSubscriptionId`|string|Azure subscription ID (**mandatory when using Azure**)|`""`|
|`osggrapherAzureResourceGroup`|string|Azure resource group name (**mandatory when using Azure**)|`""`|
|`osggrapherAzureRegion`|string|Azure region (e.g., `westeurope`)|`""`|
|`osggrapherAzureTenantId`|string|Azure AD tenant ID (optional if using default authentication)|`""`|
|`osggrapherAzureClientId`|string|Azure service principal client ID (optional if using default authentication)|`""`|
|`osggrapherAzureSecret`|string|Azure service principal secret (optional if using default authentication)|`""`|

### Display Options

|Name|Type|Description|Default|
|----|----|-----------|-------|
|`osggrapherShowDefault`|bool|Do you want to see default security group|`false`|
|`osggrapherShowInstances`|bool|Do you want to see instances/servers with their security groups|`false`|
|`osggrapherShowInterfaces`|bool|Do you want to see network interfaces/ENIs with their security groups|`false`|
|`osggrapherShowEgressAnyAnyRules`|bool|Do you want to show egress ANY ANY rules|`true`|

### Output Configuration

|Name|Type|Description|Default|
|----|----|-----------|-------|
|`osggrapherRankdir`|string|Graph direction. See <https://www.graphviz.org/doc/info/attrs.html#d:rankdir>|`LR`|
|`osggrapherDotFileToRender`|string|Path and name of generated dot file|`./CloudGrapher.dot`|
|`osggrapherFileToRender`|string|Path and name of generated image file|`./CloudGrapher.png`|
|`osggrapherRenderCsvFile`|bool|Do you want to generate a [csv file](doc/CloudGrapher.csv) of SG and SG Rules|`false`|
|`osggrapherCsvFileToRender`|string|Path and name of generated csv file|`./CloudGrapher.csv`|
|`osggrapherRenderMdFile`|bool|Do you want to generate a [markdown file](doc/CloudGrapher.md) of SG and SG Rules|`false`|
|`osggrapherMdFileToRender`|string|Path and name of generated markdown file|`./CloudGrapher.md`|

### Filtering

|Name|Type|Description|Default|
|----|----|-----------|-------|
|`osggrapherFilter`|string|String (begin with) to filter instances and security groups name. For AWS: can also filter by tag Name|`""`|

 :point_right: If you are in a mutualized environment, you'll probably want to filter information.

 To do that, you will have to use the `osggrapherFilter` parameter. For instance:
 - **OpenStack**: if all your resources names begin with the same string (e.g., WEB), filter with `osggrapherFilter: WEB`
 - **AWS**: filter by resource names or use AWS tags with Name starting with the filter string

 ```yaml
 osggrapherFilter: WEB
 ```

## Example Playbooks

### OpenStack Example

~~~yaml
---
- name: OpenStack Security group grapher
  hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - role: cloud-securitygroup-grapher
      osggrapherCloudProvider: openstack
      osggrapherCloudInfra: MyCloud
      osggrapherShowInstances: true
~~~

### AWS Example

~~~yaml
---
- name: AWS Security group grapher
  hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - role: cloud-securitygroup-grapher
      osggrapherCloudProvider: aws
      osggrapherAwsRegion: eu-west-1
      osggrapherAwsProfile: production
      osggrapherFilter: "prod-"
      osggrapherShowInstances: true
~~~

### Azure Example

~~~yaml
---
- name: Azure Security group grapher
  hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - role: cloud-securitygroup-grapher
      osggrapherCloudProvider: azure
      osggrapherAzureSubscriptionId: "12345678-1234-1234-1234-123456789012"
      osggrapherAzureResourceGroup: "prod-rg"
      osggrapherAzureRegion: "westeurope"
      osggrapherFilter: "prod-"
      osggrapherShowInstances: true
~~~

## Technical Architecture

This role uses an optimized multi-cloud template architecture for better performance and maintainability:

- **Multi-cloud support**: Unified architecture supporting OpenStack, AWS, and Azure with provider-specific data collection
- **Data normalization**: Cloud provider data is normalized to a common format before processing
- **Unified templates**: Single template system supporting all output formats (DOT/CSV/Markdown) across all providers
- **Shared macros**: Reusable Jinja2 macros in `templates/macros.j2` for consistent rule processing
- **Performance optimization**: O(1) security group lookup using pre-built dictionaries
- **Robust error handling**: Safe handling of missing interfaces, deleted security groups, and malformed data
- **Simplified maintenance**: Centralized logic eliminates code duplication

## Examples of generated images

### How to read the graph

Ellipses are *security groups.*

The red arrows represent *egress* flows: for example, the UDP stream 53 is authorized as output of SG-VPC-INTERNAL to 10.xxx.yyy.zza.

The blue arrows represent *ingress* flows: for example, tcp stream 443 is allowed as input of SG-VPC-LB from any (0.0.0.0/0)

The arrow head is always on the security group which contains the rule represented by the arrow.

### Full example

*It shows a tenant with several security groups corresponding to the different functions of the machines present in the project.*

![Example](doc/CloudGrapher.png)

### Simpler example

*It shows in particular a SG that accepts any input from any source and a SG that allows any output to any destination.*

![Example](doc/SimpleGraph.png)

### osggrapherShowDefault

With osggrapherShowDefault: true, you'll have on your graph all the SGs, included the default Openstack SG:

![Example](doc/DefaultSG.jpg)

### osggrapherShowInstances

With osggrapherShowInstances: true, you'll have on your graph all the instances (VM) within SGs used by these instances.

![Example](doc/Instances.png)

### osggrapherShowInterfaces

With osggrapherShowInterfaces: true, you'll have on your graph all the network interfaces (with their ip addresses) using each security groups.

This visualization is usefull when your instances have multiple network interfaces and you use different security group on different network interfaces.

Obviously, this visualization is easier to read when you take care to name your network interfaces with human readable names.

![Example](doc/interfaces.png)

### osggrapherRankdir

With osggrapherRankdir: LR, left to right, RL, right to left, TB, top to bottom, BT, bottom to top, you can change the way to draw the graph.

#### LR example

![Example](doc/LR.png)

#### TB example

![Example](doc/TB.png)

### Author Information

Jean-Louis FEREY
