# LILA Lab Infrastructure

## Infrastructure & Tools

This directory contains the infrastructure components that support LILA Lab's operations.

### Components

| Component | Description | Status |
|-----------|-------------|--------|
| **Discord Bot** | Community management, onboarding, ticket system | ✅ Ready |
| **Website** | Public-facing website (GitHub Pages) | ✅ Deployed at lilalab.pro.bd |
| **Scripts** | Utility scripts for deployment and maintenance | 🔜 Planned |

---

### Discord Bot

The Discord bot manages the LILA Lab community with:

- **Welcome & Onboarding** — Automatic role assignment, welcome messages
- **GitHub Integration** — Track issues, PRs, contributors
- **Ticket System** — Support tickets for contributor help
- **Contributor Tracking** — Register, track contributions, integrate with OWNERS.csv
- **Moderation** — Admin tools for server management

**Setup:**
```bash
cd discord-bot/
cp .env.example .env
# Edit .env with your bot token
pip install -r requirements.txt
python bot.py
```

**Documentation:** See `discord-bot/README.md`

---

### Website

The LILA Lab website is live at **[lilalab.pro.bd](https://lilalab.pro.bd/)** — deployed via GitHub Pages from `docs/`.

**Pages include:**
- Hero with mission statement and BENI benchmark
- XENI pipeline framework explainer
- Pipeline showcase with active/planned status
- Research paper series overview
- Contribution grid with 8 models
- Community and contact links

**Source:** See `docs/` for HTML/CSS assets, `infrastructure/website/` for the dashboard app.

---

### Scripts

Utility scripts for common operations:

```
scripts/
├── deployment/           # Deployment scripts
│   ├── deploy-website.sh
│   └── deploy-bot.sh
│
└── maintenance/          # Maintenance scripts
    ├── backup-data.sh
    └── update-deps.sh
```

---

## Environment Variables

Create a `.env` file in this directory (or in subdirectories) with:

```bash
# Discord Bot
DISCORD_TOKEN=your_bot_token
GUILD_ID=your_server_id

# GitHub Integration
GITHUB_TOKEN=your_github_token
GITHUB_REPO=LilaLABx/LILA-LAB

# Email Notifications (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

---

## Deployment Options

### Discord Bot

- **Local:** Run `python bot.py` directly
- **Railway:** Free tier available
- **Render:** Free tier available
- **VPS:** Any Linux VPS with Python 3.10+

### Website

- **GitHub Pages:** Free, automatic deployment
- **Custom Domain:** Purchase `lila-lab.org` and configure DNS

---

## Contributing to Infrastructure

Infrastructure contributions are welcome! See [`COLLABORATION.md`](../COLLABORATION.md) for the full framework.

**High-need areas:**
- Dashboard deployment and enhancements
- Discord bot features and cogs
- CI/CD automation
- Monitoring and analytics
