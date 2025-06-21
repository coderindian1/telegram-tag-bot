# Complete Step-by-Step Deployment Guide

## Phase 1: Get Your Bot Token

1. **Create Telegram Bot:**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` command
   - Choose a name: `My Tag Bot` (or any name you like)
   - Choose a username: `mytag_bot` (must end with "bot")
   - Copy the token (looks like: `1234567890:ABCDEFghijklmnop...`)
   - Save this token - you'll need it later

## Phase 2: Upload Files to GitHub

### Files to Upload (12 total):

**Core Bot Files:**
- `main.py`
- `bot.py`  
- `handlers.py`
- `database.py`
- `utils.py`
- `config.py`
- `keep_alive.py`

**Deployment Files:**
- `run_requirements.txt`
- `Dockerfile`
- `render.yaml`
- `.gitignore`
- `DEPLOYMENT_GUIDE.md`

### Upload Steps:

1. **Create GitHub Repository:**
   - Go to https://github.com
   - Click "New repository" (green button)
   - Repository name: `telegram-tag-bot`
   - Choose Public or Private
   - Don't check "Initialize with README"
   - Click "Create repository"

2. **Upload Files:**
   - Click "uploading an existing file"
   - Select ALL 12 files listed above
   - Drag and drop them or click "choose your files"
   - Commit message: `Telegram Tag Bot - Complete Package`
   - Click "Commit changes"

## Phase 3: Deploy to Render

1. **Create Render Account:**
   - Go to https://render.com
   - Sign up with GitHub (recommended)
   - Verify your email

2. **Create Web Service:**
   - Click "New +" button
   - Select "Web Service"
   - Choose "Connect a repository"
   - Select your `telegram-tag-bot` repository
   - Click "Connect"

3. **Configure Service:**
   ```
   Name: telegram-tag-bot
   Runtime: Python 3
   Build Command: pip install -r run_requirements.txt
   Start Command: python start.py
   Plan: Free
   ```

4. **Add Environment Variable:**
   - Scroll down to "Environment Variables"
   - Click "Add Environment Variable"
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: (paste your bot token from step 1)
   - Click "Save Changes"

5. **Deploy:**
   - Click "Create Web Service"
   - Wait 3-5 minutes for deployment
   - Check logs for "Bot started successfully"

## Phase 4: Test Your Bot

1. **Find Your Bot:**
   - Open Telegram
   - Search for your bot username (from step 1)
   - Click on your bot and start a conversation

2. **Test Commands:**
   - Send `/start` - Should show welcome message
   - Send `/help` - Shows all available commands

3. **Test in Groups:**
   - Add bot to a Telegram group
   - Make bot an admin (for full functionality)
   - Test `/tag Hello everyone!` - Should tag group members

## Available Bot Features

### Commands:
- `/start` - Initialize bot
- `/help` - Show help message
- `/tag [message]` - Tag all group members
- `/afk [reason]` - Set AFK status
- `/back` - Remove AFK status
- `/setemoji <emoji>` - Change tagging emoji (admin)
- `/addadmin <user>` - Add admin (owner only)
- `/removeadmin <user>` - Remove admin (owner only)
- `/broadcast <message>` - Send to all users (admin)

### Key Features:
- Smart member tagging with emoji format
- AFK system with duration tracking
- Admin management system
- Broadcasting to all users
- 24/7 operation with auto-restart
- Automatic member discovery

## Troubleshooting

**Bot not responding:**
- Check TELEGRAM_BOT_TOKEN is correct
- Verify Render service is running (green status)
- Check logs in Render dashboard

**Can't tag members:**
- Make bot an admin in the group
- Bot can only see members who have interacted with it
- This is a Telegram API limitation

**Service won't start:**
- Check all 12 files are uploaded to GitHub
- Verify run_requirements.txt contains: `python-telegram-bot==22.1`
- Check Render logs for specific errors

## Cost Information

- **GitHub:** Free for public repositories
- **Render:** Free tier includes 750 hours/month (24/7 operation)
- **Total Cost:** $0 - completely free hosting

Your bot will run 24/7 with automatic restarts and full functionality!

## Need Help?

1. Check Render service logs for errors
2. Verify bot token is correct
3. Test bot in private chat first
4. Ensure all files are uploaded to GitHub

The bot will automatically restart if it crashes and handle all group management tasks reliably.