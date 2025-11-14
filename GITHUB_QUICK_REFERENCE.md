# BCKismet GitHub Quick Reference

**🚨 CRITICAL: Always check for large files before committing!**

## Pre-Push Safety Check (MANDATORY)
```bash
# Check for large files (>50MB)
find . -type f -size +50M -not -path "./.git/*"

# Verify critical file is excluded
ls -lh forgedfate/kismet/kismet_data.json 2>/dev/null && echo "⚠️  DANGER: Large file exists!" || echo "✅ Safe"

# Check what will be committed
git diff --cached --stat
```

## Safe Commit Pattern
```bash
# 1. Add specific files only (NEVER 'git add .')
git add README.md .gitignore *.sh *.conf *.md *.desktop
git add forgedfate/kismet/http_data/js/*.js
git add forgedfate/kismet/http_data/*.html

# 2. Verify staging
git status

# 3. Commit with message
git commit -m "Description of changes"

# 4. Push to GitHub
git push github main
```

## Emergency: Large File Committed
```bash
# Remove from git history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch forgedfate/kismet/kismet_data.json' \
  --prune-empty --tag-name-filter cat -- --all

# Force push (CAUTION)
git push --force-with-lease github main
```

## Files to NEVER Commit
- `forgedfate/kismet/kismet_data.json` (635MB)
- `*.kismet` (database files)
- `*.log` (log files)
- Files over 50MB

## Quick Commands
```bash
# Check file sizes
ls -lh forgedfate/kismet/ | grep -E "(kismet_data|\.kismet)"

# Test .gitignore
git check-ignore forgedfate/kismet/kismet_data.json

# Reset if needed
git reset --hard HEAD
```

**📖 Full Guide**: See `GITHUB_WORKFLOW_GUIDE.md` for complete instructions
