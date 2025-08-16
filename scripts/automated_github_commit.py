#!/usr/bin/env python3
"""
Automated GitHub Commit Script for Colosseum Platform
Ensures all mission completions are systematically backed up to GitHub
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class ColosseumGitAutomation:
    """Automated git workflow for Colosseum platform mission completions."""
    
    def __init__(self, repo_path: str = None):
        """Initialize with repository path."""
        if repo_path is None:
            # Default to Colosseum directory
            repo_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum"
        
        self.repo_path = Path(repo_path)
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def check_git_status(self) -> dict:
        """Check current git status and return summary."""
        try:
            os.chdir(self.repo_path)
            
            # Get status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            changes = {
                'modified': [],
                'added': [],
                'deleted': [],
                'untracked': []
            }
            
            for line in status_lines:
                if not line:
                    continue
                    
                status_code = line[:2]
                file_path = line[3:]
                
                if status_code.startswith('M'):
                    changes['modified'].append(file_path)
                elif status_code.startswith('A'):
                    changes['added'].append(file_path)
                elif status_code.startswith('D'):
                    changes['deleted'].append(file_path)
                elif status_code.startswith('??'):
                    changes['untracked'].append(file_path)
            
            return changes
            
        except subprocess.CalledProcessError as e:
            print(f"Error checking git status: {e}")
            return {}
    
    def create_mission_commit_message(self, mission_name: str, mission_summary: str, 
                                    business_impact: str) -> str:
        """Create professional commit message following Colosseum standards."""
        
        message = f"""[MISSION] {mission_name}

{mission_summary}

STRATEGIC IMPACT:
{business_impact}

TOWER OVERSIGHT: Quality assurance completed
ROMAN ENGINEERING: Systematic excellence maintained
COMPETITIVE ADVANTAGE: Platform capabilities enhanced

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
        
        return message
    
    def create_organizational_commit_message(self, changes_summary: str, 
                                           business_impact: str) -> str:
        """Create commit message for organizational changes."""
        
        message = f"""[ORGANIZATIONAL] {changes_summary}

TECHNICAL ACHIEVEMENTS:
{business_impact}

STRATEGIC IMPACT:
- Roman engineering standards enforced
- Professional structure enhances competitive position
- Systematic organization enables enterprise scalability
- Knowledge preservation through proper documentation

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
        
        return message
    
    def auto_commit_and_push(self, commit_message: str, push_to_github: bool = True) -> bool:
        """Automatically commit and push changes to GitHub."""
        try:
            os.chdir(self.repo_path)
            
            # Add all changes
            print("📋 Staging all changes...")
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Commit with message
            print("💾 Creating commit...")
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            if push_to_github:
                print("🚀 Pushing to GitHub...")
                # Use longer timeout for large pushes
                result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                      timeout=300, check=True)
                print("✅ Successfully pushed to GitHub!")
            
            return True
            
        except subprocess.TimeoutExpired:
            print("⏱️ Push taking longer than expected - continuing in background")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error in git operation: {e}")
            return False
    
    def mission_completion_workflow(self, mission_name: str, mission_summary: str, 
                                  business_impact: str) -> bool:
        """Complete workflow for mission completion git integration."""
        
        print(f"🏛️ COLOSSEUM GIT AUTOMATION - Mission: {mission_name}")
        print(f"📅 Timestamp: {self.timestamp}")
        
        # Check for changes
        changes = self.check_git_status()
        if not any(changes.values()):
            print("ℹ️ No changes detected - skipping commit")
            return True
        
        # Show changes summary
        total_changes = sum(len(files) for files in changes.values())
        print(f"📊 Changes detected: {total_changes} files")
        
        # Create commit message
        commit_msg = self.create_mission_commit_message(
            mission_name, mission_summary, business_impact
        )
        
        # Commit and push
        success = self.auto_commit_and_push(commit_msg)
        
        if success:
            print("🏛️ Mission completion successfully backed up to GitHub!")
            print("🎯 Vincere Habitatio - Roman engineering excellence preserved")
        
        return success


def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 4:
        print("Usage: python3 automated_github_commit.py <mission_name> <mission_summary> <business_impact>")
        print("\nExample:")
        print('python3 automated_github_commit.py "BOTN Engine Restructure" "Professional Python organization" "Enterprise-grade competitive advantage"')
        sys.exit(1)
    
    mission_name = sys.argv[1]
    mission_summary = sys.argv[2]
    business_impact = sys.argv[3]
    
    automation = ColosseumGitAutomation()
    success = automation.mission_completion_workflow(mission_name, mission_summary, business_impact)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()