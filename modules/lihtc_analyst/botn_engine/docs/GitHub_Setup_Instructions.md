# GitHub Repository Setup Instructions for CALIHTCScorer

## Step 1: Create Repository on GitHub

1. Go to https://github.com and log in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Fill in the following:
   - **Repository name**: `CALIHTCScorer`
   - **Description**: "LIHTC Site Scoring System - Analyzes potential Low-Income Housing Tax Credit sites for California CTCAC scoring"
   - **Visibility**: Choose Private or Public based on your preference
   - **DO NOT** initialize with README, .gitignore, or license (we already have these locally)
5. Click "Create repository"

## Step 2: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these in your terminal:

```bash
# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/CALIHTCScorer.git

# Verify the remote was added
git remote -v

# Push the main branch
git push -u origin main

# Push the current feature branch
git push -u origin amenity-scoring-fix
```

## Step 3: Set Up GitHub CLI (Optional but Recommended)

To use the workflow commands from CLAUDE.md (nb, ppr, cpr, etc.), install GitHub CLI:

```bash
# On macOS with Homebrew
brew install gh

# Authenticate with GitHub
gh auth login
```

## Step 4: Configure Git User (if not already done)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 5: Verify Everything Works

```bash
# Check current status
git status

# Check all branches (local and remote)
git branch -a

# Test pushing changes
echo "# Test" >> test.txt
git add test.txt
git commit -m "Test GitHub connection"
git push
rm test.txt
git add test.txt
git commit -m "Remove test file"
git push
```

## Current Repository State

- **Main branch**: Contains all work up to transit enhancement
- **amenity-scoring-fix branch**: Contains CTCAC 2025 4% LIHTC amenity scoring updates (uncommitted)

## Next Steps

1. Create the GitHub repository following Step 1
2. Run the commands in Step 2 to connect your local repo
3. Consider installing GitHub CLI for enhanced workflow
4. Start following the TDD workflow from CLAUDE.md for future development

## Repository Structure
```
CALIHTCScorer/
├── src/                    # Core application code
│   ├── core/              # Main analysis engine
│   ├── analyzers/         # Specialized analyzers
│   └── utils/             # Utility functions
├── scripts/               # Data update scripts
├── data/                  # Local data storage
├── config/                # Configuration files
├── logs/                  # Application logs
├── README.md              # Project documentation
├── HANDOFF.md            # Detailed development notes
└── requirements.txt       # Python dependencies
```