# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - ALPHA

### Added

- **Azure Support**: Complete Azure cloud provider integration
  - Azure NSG (Network Security Groups) data collection via `azure.azcollection`
  - Azure VMs and Network Interfaces support
  - Azure-specific data normalization with priority handling
  - Azure Service Tags support (Internet, VirtualNetwork, AzureLoadBalancer)
  - Multi-port and multi-source Azure rules handling
- **Multi-Cloud Architecture**: Unified template system supporting OpenStack, AWS, and Azure
  - Single template system for all output formats (DOT/CSV/Markdown)
  - Provider-agnostic data normalization
  - Shared Jinja2 macros for consistent rule processing
  - Optimized security group lookup with O(1) performance
- **Test Infrastructure**: Comprehensive test suite for all providers
  - Azure test environment deployment (3-tier architecture)
  - OpenStack and AWS test scenarios
  - Automated cleanup scripts for all providers
- **Enhanced Documentation**: 
  - Complete Azure configuration examples
  - Multi-cloud architecture documentation
  - Test scenarios and troubleshooting guides
  - Alpha version warnings and disclaimers

### Changed

- **Provider Validation**: Extended to support `azure` in addition to `openstack` and `aws`
- **Requirements**: Added `azure.azcollection` collection dependency
- **Documentation**: All content translated from French to English
- **Architecture**: Refactored for better multi-cloud extensibility

### Security

- **Credential Protection**: Azure secrets properly masked in logs with `no_log` directives
- **Input Validation**: Mandatory parameter validation for all cloud providers

### Notes

- ⚠️ **ALPHA VERSION**: This release is for development and testing only
- 🔴 **NOT PRODUCTION READY**: No serious testing has been conducted yet
- All providers (OpenStack, AWS, Azure) require thorough testing before production use
