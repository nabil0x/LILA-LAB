# LILA Lab Infrastructure

## Infrastructure & Tools

This directory contains the infrastructure components that support LILA Lab's operations.

### Components

| Component | Description | Status |
|-----------|-------------|--------|
| **Discord Bot** | Community management, onboarding, ticket system | ✅ Ready |
| **Website** | Public-facing website (GitHub Pages) | 🔜 Planned |
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

The LILA Lab website will be hosted on GitHub Pages at `lila-lab.org`.

**Planned Pages:**
- Home — Lab overview and mission
- Research — Paper series and publications
- Pipelines — XENI pipeline showcase
- Contribute — How to contribute
- Team — Contributors and collaborators
- Contact — Get in touch

**Status:** Not yet deployed. See `communications/P0_P1_COMMUNITY_SETUP.md`.

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
GITHUB_REPO=nabil0x/LILA-LAB

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

Infrastructure contributions are welcome! See `COLLABORATION.md` for the full framework.

**High-need areas:**
- Website development (HTML/CSS/JS)
- Discord bot features
- Deployment automation
- Monitoring and analytics
