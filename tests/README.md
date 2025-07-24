# Tests Scripts for Cloud Security Group Grapher

This directory contains test scripts to deploy realistic cloud environments and validate the cloud-securitygroup-grapher role across OpenStack, AWS, and Azure.

## Test Architecture

The scripts deploy a **realistic 3-tier architecture**:

```
Internet  →  [Web Tier]  →  [App Tier]  →  [Database Tier]
             HTTP/HTTPS      API calls       DB queries
```

### Deployed Components

| Tier | Instance | Security Group | Open Ports |
|------|----------|----------------|------------|
| **Web** | `sgtest-web-server` | `sgtest-web-sg` | 22 (SSH), 80 (HTTP), 443 (HTTPS) |
| **App** | `sgtest-app-server` | `sgtest-app-sg` | 22 (SSH), 8080 (API), 8443 (API secure) |
| **Database** | `sgtest-db-server` | `sgtest-db-sg` | 22 (SSH), 3306 (MySQL), 5432 (PostgreSQL) |

### Security Flows

- **Internet → Web** : Public HTTP/HTTPS access
- **Web → App** : API access from web tier only
- **App → Database** : Database access from app tier only
- **SSH** : SSH access from internet (for administration)

## Usage

### 🔧 Prerequisites

#### OpenStack
```bash
# clouds.yaml configuration
mkdir -p ~/.config/openstack
cat > ~/.config/openstack/clouds.yaml << EOF
clouds:
  testcloud:
    auth:
      auth_url: https://your-openstack-endpoint/v3
      username: your-username
      password: your-password
      project_name: your-project
      user_domain_name: Default
      project_domain_name: Default
    region_name: your-region
EOF
```

#### AWS
```bash
# AWS CLI configuration
aws configure
# OR create ~/.aws/credentials :
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = eu-west-1
```

### 📝 Customization

Before executing, **modify the variables** in the playbooks:

#### `deploy-openstack.yml`
```yaml
vars:
  cloud_name: "testcloud"        # Your cloud name in clouds.yaml
  key_name: "test-key"           # Your OpenStack SSH key name
  flavor: "s1-2"                 # Instance flavor (ex: m1.small)
  image: "Ubuntu 22.04"          # OS image name
  network: "Ext-Net"             # External network name
```

#### `deploy-aws.yml`
```yaml
vars:
  aws_region: "eu-west-1"        # AWS region
  aws_profile: "default"         # AWS profile
  key_name: "test-key"           # Your EC2 Key Pair name
  ami_id: "ami-0c02fb55956c7d316" # AMI ID for your region
```

### 🚀 Complete Test Workflow

#### OpenStack Test

```bash
# 1. Deploy test environment
ansible-playbook tests/deploy-openstack.yml

# 2. Test the role
ansible-playbook tests/test-openstack-role.yml

# 3. Check generated files
ls -la openstack-test.*
# openstack-test.png  → Visualization graph
# openstack-test.csv  → CSV rules export
# openstack-test.md   → Markdown export
# openstack-test.dot  → Graphviz source

# 4. Clean up environment
ansible-playbook tests/cleanup-openstack.yml
```

#### AWS Test

```bash
# 1. Deploy test environment
ansible-playbook tests/deploy-aws.yml

# 2. Test the role
ansible-playbook tests/test-aws-role.yml

# 3. Check generated files
ls -la aws-test.*
# aws-test.png  → Visualization graph
# aws-test.csv  → CSV rules export
# aws-test.md   → Markdown export
# aws-test.dot  → Graphviz source

# 4. Clean up environment
ansible-playbook tests/cleanup-aws.yml
```

#### Azure Test

```bash
# 1. Deploy test environment
ansible-playbook tests/deploy-azure.yml

# 2. Test the role
ansible-playbook tests/test-azure-role.yml

# 3. Check generated files
ls -la azure-test.*
# azure-test.png  → Visualization graph
# azure-test.csv  → CSV rules export
# azure-test.md   → Markdown export
# azure-test.dot  → Graphviz source

# 4. Clean up environment
ansible-playbook tests/cleanup-azure.yml
```

### 📊 Expected Results

#### Generated Graph

The generated PNG should show:
- **3 ellipses** : sgtest-web-sg, sgtest-app-sg, sgtest-db-sg
- **Blue arrows** (ingress) : Internet → Web, Web → App, App → DB
- **Instances** in security groups (if `osggrapherShowInstances: true`)

#### Generated CSV

```csv
"Security group";"Direction";"IP type";"Protocol";"Port";"Remote partner";"Provider"
"sgtest-web-sg";"ingress";"IPv4";"tcp";"80";"0.0.0.0/0";"openstack"
"sgtest-web-sg";"ingress";"IPv4";"tcp";"443";"0.0.0.0/0";"openstack"
"sgtest-app-sg";"ingress";"IPv4";"tcp";"8080";"sgtest-web-sg";"openstack"
...
```

## Troubleshooting

### Common Errors

#### OpenStack
```bash
# Error: "Cloud testcloud not found"
# → Check your clouds.yaml file

# Error: "Flavor not found"
# → List available flavors:
openstack flavor list

# Error: "Image not found"  
# → List available images:
openstack image list
```

#### AWS
```bash
# Error: "Unable to locate credentials"
# → Check aws configure or ~/.aws/credentials

# Error: "AMI not found"
# → Find AMI for your region:
aws ec2 describe-images --owners amazon --filters "Name=name,Values=amzn2-ami-hvm-*"

# Error: "Key pair not found"
# → Create a key pair:
aws ec2 create-key-pair --key-name test-key
```

### Manual Validation

#### Verify OpenStack Deployment
```bash
openstack server list | grep sgtest
openstack security group list | grep sgtest
openstack security group rule list sgtest-web-sg
```

#### Verify AWS Deployment
```bash
aws ec2 describe-instances --filters "Name=tag:Name,Values=sgtest-*"
aws ec2 describe-security-groups --filters "Name=group-name,Values=sgtest-*"
```

## Estimated Costs

### OpenStack (OVH Cloud with $200 credits)
- 3 s1-2 instances : ~€0.50/hour × 3 = €1.50/hour
- **1-hour test** : ~€1.50 (remaining $198.50 credits)

### AWS (Free Tier)
- 3 t3.micro instances : 750h free/month
- **Multiple tests possible** within Free Tier limits

## Important Notes

⚠️ **Don't forget to clean up** after your tests to avoid costs!

✅ **Cleanup scripts** automatically remove all created resources.

🔧 **Adapt variables** according to your environment before executing.

📈 **Recommended tests** : Execute on both providers to validate multi-cloud compatibility.