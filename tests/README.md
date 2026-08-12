# Tests Scripts for Cloud Security Group Grapher

This directory contains test scripts to deploy realistic cloud environments and validate the cloud-securitygroup-grapher role across OpenStack, AWS, and Azure.

## ✅ **Test Status**

- **AWS**: ✅ **VALIDATED** - Successfully tested with 3-tier architecture + bastion
- **OpenStack**: 🟡 Untested - Scripts available but not validated
- **Azure**: 🟡 Untested - Scripts available but not validated

## Test Architecture

### AWS (Validated)

Deploys a **4-tier architecture with bastion** for secure access:

```
Internet  →  [Bastion]  →  [Load Balancer]  →  [Web Tier (x2)]  →  [Database Tier]
             SSH jump       HTTP/HTTPS          App servers           DB server
```

#### Deployed Components (AWS)

| Tier | Instances | Security Group | Ingress Rules |
|------|-----------|----------------|---------------|
| **Bastion** | `sgtest-bastion` | `sgtest-bastion-sg` | SSH (22) from Internet |
| **Load Balancer** | `sgtest-lb` | `sgtest-lb-sg` | HTTP (80), HTTPS (443) from Internet<br>SSH (22) from bastion only |
| **Web** | `sgtest-web-1`<br>`sgtest-web-2` | `sgtest-web-sg` | HTTP (8080), HTTPS (8443) from LB only<br>SSH (22) from bastion only |
| **Database** | `sgtest-db` | `sgtest-db-sg` | MySQL (3306), PostgreSQL (5432), Redis (6379) from Web only<br>SSH (22) from bastion only |

#### Security Flows (AWS)

- **Internet → Bastion** : SSH access for administration (jump host)
- **Internet → Load Balancer** : Public HTTP/HTTPS traffic
- **Load Balancer → Web** : Proxied traffic to application servers
- **Web → Database** : Database queries from application tier only
- **Bastion → All** : SSH access through bastion (ProxyJump pattern)
- **Network Isolation**: VPC with custom subnet, Internet Gateway, and route table

### OpenStack / Azure (Not Yet Tested)

3-tier architecture similar to AWS but without bastion (legacy scripts).

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

### 📝 Configuration

#### AWS (Recommended - Validated)

Variables are in `group_vars/all/aws.yml`. Customize before running:

```yaml
aws_region: "eu-west-3"              # Your AWS region
aws_profile: "default"               # AWS profile from ~/.aws/credentials
aws_key_name: "sgtest-key"           # EC2 key pair name (must exist)
aws_instance_type: "t3.micro"        # Instance type (Free Tier)
aws_ami_id: "ami-0162ba22edf21828a"  # Amazon Linux 2 AMI for your region
aws_prefix: "sgtest"                 # Resource naming prefix
```

Create EC2 key pair if needed:
```bash
aws ec2 create-key-pair --key-name sgtest-key --query 'KeyMaterial' --output text > ~/.ssh/sgtest-key.pem
chmod 400 ~/.ssh/sgtest-key.pem
```

#### OpenStack (Legacy - Not Validated)

Modify variables directly in `deploy-openstack.yml`:
```yaml
cloud_name: "testcloud"        # Your cloud name in clouds.yaml
key_name: "test-key"           # Your OpenStack SSH key name
flavor: "s1-2"                 # Instance flavor
image: "Ubuntu 22.04"          # OS image name
network: "Ext-Net"             # External network name
```

#### Azure (Legacy - Not Validated)

Modify variables directly in `deploy-azure.yml`
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