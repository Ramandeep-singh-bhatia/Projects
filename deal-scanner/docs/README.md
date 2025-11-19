# Deal Scanner Documentation

Welcome to the complete documentation for the Multi-Retail Deal Scanner system.

## Documentation Index

### Getting Started
- **[User Guide](USER_GUIDE.md)** - Complete guide for end users
  - Installation and setup
  - Configuration
  - Running the scanner
  - Understanding notifications
  - Managing watchlists
  - FAQ

### Deployment
- **[Deployment Guide](DEPLOYMENT.md)** - How to deploy and run 24/7
  - Local deployment
  - Linux server (systemd)
  - Docker deployment
  - Cloud platforms (AWS, GCP, Oracle, etc.)
  - Raspberry Pi
  - Monitoring & maintenance

### Development
- **[Developer Guide](DEVELOPER_GUIDE.md)** - For developers and contributors
  - Development setup
  - Code structure
  - Adding new retailers
  - Custom agent development
  - Database operations
  - Testing
  - Contributing guidelines

### Reference
- **[Architecture Documentation](ARCHITECTURE.md)** - System design and architecture
  - System overview
  - Architecture patterns
  - Component design
  - Data flow
  - Database schema
  - Agent system
  - Scalability considerations

- **[Configuration Reference](CONFIGURATION.md)** - Complete configuration guide
  - Environment variables
  - Settings file
  - Watchlist configuration
  - Rate limiting
  - Advanced options

### Support
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions
  - Quick diagnostics
  - Common problems
  - Installation issues
  - Runtime errors
  - Notification problems
  - Scraping issues
  - Performance tuning

## Quick Links

### By Role

**I'm a User** (Just want to use it)
1. Start with [User Guide](USER_GUIDE.md)
2. Then [Configuration Reference](CONFIGURATION.md)
3. Refer to [Troubleshooting](TROUBLESHOOTING.md) if needed

**I'm Deploying to Production**
1. Read [User Guide](USER_GUIDE.md) first
2. Follow [Deployment Guide](DEPLOYMENT.md)
3. Review [Configuration Reference](CONFIGURATION.md)

**I'm a Developer** (Want to extend/modify)
1. Read [Architecture Documentation](ARCHITECTURE.md)
2. Follow [Developer Guide](DEVELOPER_GUIDE.md)
3. See [User Guide](USER_GUIDE.md) for usage

### By Task

**Installing for the First Time**
→ [User Guide - Installation](USER_GUIDE.md#installation)

**Setting Up Telegram Bot**
→ [User Guide - Telegram Setup](USER_GUIDE.md#setting-up-telegram-required)

**Configuring Products to Watch**
→ [Configuration Reference - Watchlist](CONFIGURATION.md#watchlist-configuration)

**Deploying to a Server**
→ [Deployment Guide - Linux Server](DEPLOYMENT.md#linux-server-systemd)

**Running with Docker**
→ [Deployment Guide - Docker](DEPLOYMENT.md#docker-deployment)

**Adding a New Retailer**
→ [Developer Guide - Adding Retailer](DEVELOPER_GUIDE.md#adding-a-new-retailer)

**Fixing Common Errors**
→ [Troubleshooting Guide](TROUBLESHOOTING.md#common-issues)

**Understanding Deal Scores**
→ [User Guide - Deal Scoring](USER_GUIDE.md#understanding-deal-score)

**Optimizing Performance**
→ [Configuration Reference - Performance Tuning](CONFIGURATION.md#performance-tuning)

## Documentation Structure

```
docs/
├── README.md              # This file - Documentation index
├── USER_GUIDE.md         # End user documentation
├── DEPLOYMENT.md         # Deployment and operations
├── DEVELOPER_GUIDE.md    # Development documentation
├── ARCHITECTURE.md       # Technical architecture
├── CONFIGURATION.md      # Configuration reference
└── TROUBLESHOOTING.md    # Problem solving guide
```

## Documentation Standards

All documentation follows these standards:

- **Clear Examples**: Every concept includes working code examples
- **Step-by-Step**: Installation and setup are broken into simple steps
- **Screenshots**: Where helpful (for GUI operations)
- **Troubleshooting**: Common issues addressed inline
- **Cross-Referenced**: Related topics are linked
- **Up-to-Date**: Maintained with code changes

## Contributing to Documentation

Found an error or want to improve the docs?

1. **Small Fixes**: Open an issue or PR directly
2. **Major Changes**: Discuss in an issue first
3. **New Sections**: Follow existing structure and style

### Documentation Style Guide

- Use clear, simple language
- Include examples for all concepts
- Provide command-line examples with expected output
- Link to related sections
- Keep formatting consistent
- Test all code examples

## Getting Help

- **Documentation Issue**: [Open GitHub Issue](../issues)
- **Question**: Check [User Guide FAQ](USER_GUIDE.md#faq)
- **Bug**: [Troubleshooting Guide](TROUBLESHOOTING.md) first
- **Feature Request**: [GitHub Discussions](../discussions)

## Version Information

- **Current Version**: 1.0.0
- **Last Updated**: 2025-01-17
- **Compatibility**: Python 3.11+

## License

This documentation is part of the Deal Scanner project and is licensed under the MIT License.

---

**Happy Reading! Let us know how we can improve these docs.** 📚
