# BCKismet GitHub Workflow Guide

**Reference Guide for AI Dev and User - GitHub Push Protocol**

## 🚨 CRITICAL: Pre-Push Checklist

### **ALWAYS CHECK BEFORE ANY COMMIT:**

1. **Large File Detection**
   ```bash
   # Check for files over 50MB (GitHub limit is 100MB)
   find . -type f -size +50M -not -path "./.git/*"
   
   # Check specific problematic files
   ls -lh forgedfate/kismet/kismet_data.json 2>/dev/null || echo "✅ kismet_data.json not found"
   ls -lh *.kismet 2>/dev/null || echo "✅ No .kismet files found"
   ```

2. **Verify .gitignore is Working**
   ```bash
   git status --ignored
   ```

3. **Check What Will Be Committed**
   ```bash
   git diff --cached --stat
   git diff --cached --name-only
   ```

## 📋 Standard GitHub Push Workflow

### **Step 1: Pre-Commit Validation**
```bash
# 1. Check for large files
find . -type f -size +50M -not -path "./.git/*"

# 2. Verify .gitignore exclusions
git status --ignored | grep -E "(kismet_data\.json|\.kismet|\.log)"

# 3. Check staged changes
git diff --cached --stat
```

### **Step 2: Safe Commit Process**
```bash
# 1. Stage only specific files (NEVER use 'git add .')
git add README.md
git add .gitignore
git add run-kismet.sh
git add forgedfate/kismet_minimal.conf
git add forgedfate/kismet_working.conf
# ... add other specific files as needed

# 2. Verify what's staged
git status

# 3. Commit with descriptive message
git commit -m "Descriptive commit message

- Specific change 1
- Specific change 2
- Specific change 3"
```

### **Step 3: Push to GitHub**
```bash
# 1. Push to GitHub remote
git push github main

# 2. If force push needed (ONLY after history rewrite)
git push --force-with-lease github main
```

## 🚫 FILES THAT MUST NEVER BE COMMITTED

### **Large Data Files**
- `forgedfate/kismet/kismet_data.json` (635MB - CRITICAL)
- `*.kismet` (Database files)
- `*.kismet-journal` (Database journals)
- Any file over 50MB

### **Temporary/Runtime Files**
- `*.log` files
- `/tmp/kismet-launch-*.sh`
- `__pycache__/` directories
- `.venv/` virtual environments

### **System/IDE Files**
- `.DS_Store` (macOS)
- `Thumbs.db` (Windows)
- `.vscode/`, `.idea/` (IDE configs)

## 🛡️ Emergency Procedures

### **If Large File Accidentally Committed**
```bash
# 1. Remove from staging (if not yet committed)
git reset HEAD forgedfate/kismet/kismet_data.json

# 2. Remove from last commit (if just committed)
git reset --soft HEAD~1
git reset HEAD forgedfate/kismet/kismet_data.json
git commit -m "Fixed commit message"

# 3. Remove from git history (if already pushed)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch forgedfate/kismet/kismet_data.json' \
  --prune-empty --tag-name-filter cat -- --all
git push --force-with-lease github main
```

### **If Push Rejected Due to Large Files**
```bash
# 1. Check what files are causing issues
git ls-files | xargs ls -lh | sort -k5 -hr | head -10

# 2. Remove problematic files
git rm --cached forgedfate/kismet/kismet_data.json
git commit -m "Remove large data file"

# 3. Update .gitignore and commit
echo "forgedfate/kismet/kismet_data.json" >> .gitignore
git add .gitignore
git commit -m "Update .gitignore to exclude large data files"

# 4. Push again
git push github main
```

## 📁 Recommended File Categories for Commits

### **Always Safe to Commit**
- Configuration files (`*.conf`)
- Scripts (`*.sh`)
- Documentation (`*.md`)
- Source code (`*.js`, `*.html`, `*.css`)
- Desktop files (`*.desktop`)

### **Commit with Caution**
- Binary files (check size first)
- Compiled files (usually should be excluded)
- Log files (usually should be excluded)

### **Never Commit**
- Database files (`*.kismet`, `*.db`)
- Large data files (`*_data.json`)
- Temporary files (`*.tmp`, `*.temp`)
- Virtual environments (`.venv/`)

## 🔧 .gitignore Maintenance

### **Current Critical Exclusions**
```gitignore
# Large Kismet data files - CRITICAL
kismet_data.json
forgedfate/kismet/kismet_data.json
*.kismet
*.kismet-journal

# Large data files (GitHub 100MB limit)
*.json
!forgedfate/kismet/http_data/js/*.js
!package.json
```

### **Verify .gitignore is Working**
```bash
# Test if files are properly ignored
git check-ignore forgedfate/kismet/kismet_data.json
# Should output the file path if properly ignored
```

## 🎯 Quick Reference Commands

### **Pre-Push Safety Check**
```bash
# One-liner safety check
find . -type f -size +50M -not -path "./.git/*" && echo "⚠️  LARGE FILES FOUND" || echo "✅ No large files"
```

### **Safe Add Pattern**
```bash
# Add only specific file types
git add *.md *.sh *.conf *.desktop
git add forgedfate/kismet/http_data/js/*.js
git add forgedfate/kismet/http_data/*.html
```

### **Emergency Reset**
```bash
# Reset everything if something goes wrong
git reset --hard HEAD
git clean -fd
```

## 📞 Contact Protocol

### **For AI Dev**
- Always run pre-push checklist before any git operations
- Reference this guide for all GitHub interactions
- If unsure, ask user before proceeding with potentially destructive operations

### **For User**
- Reference this guide before manual git operations
- Use the provided commands for safety checks
- Keep this guide updated as project evolves

---

**Last Updated**: November 2024  
**Version**: 1.0  
**Critical Files to Never Commit**: `forgedfate/kismet/kismet_data.json` (635MB)
