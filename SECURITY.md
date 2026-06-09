# Security Policy

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Email: **n7for8572@gmail.com**

Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Python version, OS, fastvk version
- Proof of concept (if applicable)

### Response timeline

| Stage | Time |
|---|---|
| Initial response | 48 hours |
| Investigation | 7 days |
| Fix & coordinated disclosure | 30–90 days |

## Security Best Practices for Users

### Store tokens in environment variables

```python
# ✅
import os
bot = FastVK(token=os.environ["VK_TOKEN"], group_id=int(os.environ["VK_GROUP_ID"]))

# ❌
bot = FastVK(token="vk1.a.hardcoded_token", group_id=123456789)
```

### Keep fastvk up to date

```bash
pip install --upgrade fastvk
```

### Run security checks on your project

```bash
pip install safety bandit
safety check
bandit -r your_bot/
```

## Supported Versions

| Version | Supported |
|---|---|
| latest | ✅ |
| older  | ❌ |

Only the latest release receives security fixes.
