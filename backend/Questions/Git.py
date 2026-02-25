from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What command is used to set your name across all repositories on your system?",
    "options": {
      "A": "git set user.name \"Name\"",
      "B": "git config --global user.name \"Name\"",
      "C": "git init user.name \"Name\"",
      "D": "git config user.name \"Name\""
    },
    "answer": "B"
  },
  {
    "question": "True or False: Git is a centralized version control system.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which file is used to specify patterns of file names that Git should ignore?",
    "options": {
      "A": ".gitinclude",
      "B": ".config",
      "C": ".gitignore",
      "D": ".gitconfig"
    },
    "answer": "C"
  },
  {
    "question": "Identify TWO areas in the Git architecture where files reside before a commit:",
    "options": {
      "A": "Working Directory",
      "B": "Staging Area (Index)",
      "C": "Virtual Archive",
      "D": "Global Cache"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: git init creates a hidden .git directory to store repository metadata.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to create a 'Tag' to mark a specific release point?",
    "options": {
      "A": "git mark v1.0",
      "B": "git tag v1.0",
      "C": "git label v1.0",
      "D": "git release v1.0"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Lightweight tags are just pointers to specific commits.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO types of tags in Git:",
    "options": {
      "A": "Lightweight",
      "B": "Annotated",
      "C": "Encrypted",
      "D": "Remote-only"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: By default, git push does not transfer tags to remote servers.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Cherry-picking' in Git?",
    "options": {
      "A": "Deleting old branches.",
      "B": "Applying a specific commit from one branch to another.",
      "C": "Renaming a project.",
      "D": "Selecting which files to ignore."
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to remove untracked files from the working directory?",
    "options": {
      "A": "git rm",
      "B": "git clean",
      "C": "git reset",
      "D": "git delete"
    },
    "answer": "B"
  },
  {
    "question": "True or False: git submodule allows you to keep another Git repository as a subdirectory of your own.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO commands help in resolving merge conflicts?",
    "options": {
      "A": "git mergetool",
      "B": "git status (to see conflicting files)",
      "C": "git solve",
      "D": "git auto-fix"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What does git log --oneline --graph --all do?",
    "options": {
      "A": "Deletes the log.",
      "B": "Shows a visual, compact representation of all branch histories and merges.",
      "C": "Shows only the first commit.",
      "D": "Lists all contributors."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The git reflog tracks every time the HEAD of any branch is updated locally.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Where does Git store its data objects?",
    "options": {
      "A": ".git/objects",
      "B": ".git/data",
      "C": ".git/refs",
      "D": "bin/git"
    },
    "answer": "A"
  },
  {
    "question": "True or False: Git uses a 'Blob' object to store the contents of a file.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are Git object types?",
    "options": {
      "A": "Commit",
      "B": "Tree",
      "C": "Index",
      "D": "Folder"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Tree' object in Git represents a directory/folder structure.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Index' in Git?",
    "options": {
      "A": "The main branch.",
      "B": "Another name for the Staging Area.",
      "C": "A search tool.",
      "D": "A list of all tags."
    },
    "answer": "B"
  },
  {
    "question": "True or False: Git compression helps reduce the size of the repository on disk.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to optimize and compress the local repository?",
    "options": {
      "A": "git compress",
      "B": "git gc (Garbage Collection)",
      "C": "git pack",
      "D": "git clean"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO things stored in a 'Commit' object:",
    "options": {
      "A": "Author information",
      "B": "Pointer to a 'Tree' object",
      "C": "Computer hardware ID",
      "D": "Internet IP address"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A Git commit is immutable; you cannot technically 'change' it, only create a new one.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of the .git/refs directory?",
    "options": {
      "A": "Stores the actual file content.",
      "B": "Stores pointers to commits (branches and tags).",
      "C": "Stores the global configuration.",
      "D": "Stores the log files."
    },
    "answer": "B"
  },
  {
    "question": "Which command allows you to view the configuration settings for the current repository?",
    "options": {
      "A": "git config --list",
      "B": "git show config",
      "C": "git status",
      "D": "git info"
    },
    "answer": "A"
  },
  {
    "question": "True or False: You should commit frequently with small, logical changes.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO popular Git branching models:",
    "options": {
      "A": "Gitflow",
      "B": "Trunk-based Development",
      "C": "Waterfall-branching",
      "D": "Loop-back"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Commit messages should ideally start with a short summary line followed by a more detailed description.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command creates an alias st for status?",
    "options": {
      "A": "git alias st status",
      "B": "git config --global alias.st status",
      "C": "git set st status",
      "D": "git alias.st = status"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Git can be used without an internet connection.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the command to see which files are currently in the staging area?",
    "options": {
      "A": "git status",
      "B": "git ls-files --stage",
      "C": "git list staged",
      "D": "git show stage"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO ways to remove a file from Git tracking:",
    "options": {
      "A": "git rm <file> (Removes from disk and Git)",
      "B": "git rm --cached <file> (Removes from Git, keeps on disk)",
      "C": "git ignore <file>",
      "D": "git delete <file>"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: It is recommended to use the main branch only for stable, production-ready code.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command shows the manual/help page for the commit command?",
    "options": {
      "A": "git help commit",
      "B": "git commit --help",
      "C": "git manual commit",
      "D": "git show-help commit"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to search for a string in the codebase history?",
    "options": {
      "A": "git search",
      "B": "git grep",
      "C": "git find",
      "D": "git scan"
    },
    "answer": "B"
  },
  {
    "question": "True or False: git stash apply keeps the changes in the stash after applying them.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are used to reference the 'parent' of the current commit?",
    "options": {
      "A": "HEAD^",
      "B": "HEAD~1",
      "C": "HEAD-parent",
      "D": "PREV"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: git remote prune origin removes local references to remote branches that no longer exist.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the result of git checkout -?",
    "options": {
      "A": "Deletes the current branch.",
      "B": "Switches back to the previously checked-out branch.",
      "C": "Resets all files.",
      "D": "Switches to the root commit."
    },
    "answer": "B"
  },
  {
    "question": "True or False: git archive is used to create a zip or tar file of the repository at a specific point.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to rename a file in both the directory and the Git index?",
    "options": {
      "A": "git rename",
      "B": "git mv",
      "C": "git move",
      "D": "git change"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO methods to update your local main branch with changes from origin/main:",
    "options": {
      "A": "git pull origin main",
      "B": "git fetch origin followed by git merge origin/main",
      "C": "git push origin main",
      "D": "git commit --sync"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Dangling Commit' is a commit that is no longer reachable from any branch or tag.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command displays the current Git version installed?",
    "options": {
      "A": "git version",
      "B": "git --version",
      "C": "git info",
      "D": "git -v"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to discard all local changes and reset to the remote's version?",
    "options": {
      "A": "git reset --hard origin/main",
      "B": "git reset --soft origin/main",
      "C": "git fetch --force",
      "D": "git undo all"
    },
    "answer": "A"
  },
  {
    "question": "True or False: Git can handle line ending differences between Windows (CRLF) and Linux (LF) automatically.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common GUI clients for Git:",
    "options": {
      "A": "Sourcetree",
      "B": "GitKraken",
      "C": "Photoshop",
      "D": "Excel"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: git cherry-pick creates a duplicate of the original commit on the current branch.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does the .git/HEAD file contain?",
    "options": {
      "A": "The project name.",
      "B": "A reference to the current branch.",
      "C": "The user's password.",
      "D": "The list of all contributors."
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to change the commit message of a commit that is NOT the most recent (interactive)?",
    "options": {
      "A": "git rebase -i",
      "B": "git change-msg",
      "C": "git commit --amend",
      "D": "git fix-history"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git checkout <commit_hash> puts you in a 'Detached HEAD' state.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO ways to view stashed changes without applying them:",
    "options": {
      "A": "git stash list",
      "B": "git stash show -p",
      "C": "git stash peek",
      "D": "git stash view"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: The .git folder should always be included when uploading your project to a web host for production.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which command allows you to view the 'help' for any Git command directly in the terminal?",
    "options": {
      "A": "git <command> --help",
      "B": "man git-<command>",
      "C": "git show help",
      "D": "git guide"
    },
    "answer": "A"
  },
  {
    "question": "Which command allows you to rename the current branch you are on?",
    "options": {
      "A": "git branch -m <new_name>",
      "B": "git branch -r <new_name>",
      "C": "git rename <new_name>",
      "D": "git move <new_name>"
    },
    "answer": "A"
  },
  {
    "question": "True or False: A 'Topic Branch' is a short-lived branch used to develop a single specific feature.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are common Git branching models?",
    "options": {
      "A": "Gitflow",
      "B": "Trunk-based Development",
      "C": "Waterfall Flow",
      "D": "Spiral Branching"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: In Trunk-based Development, developers make long-lived feature branches that last for weeks.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which command lists all branches that have already been merged into the current branch?",
    "options": {
      "A": "git branch --merged",
      "B": "git branch --done",
      "C": "git list --merged",
      "D": "git branch -a"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git checkout -b <name> is a shorthand for creating a branch and then switching to it.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO options can be used with git branch to delete a branch?",
    "options": {
      "A": "-d (safe delete)",
      "B": "-D (force delete)",
      "C": "-x",
      "D": "--remove"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Tracking Branch' is a local branch that has a direct relationship to a remote branch.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to set an existing local branch to track a remote branch?",
    "options": {
      "A": "git branch -u <remote>/<branch>",
      "B": "git branch --track <remote>/<branch>",
      "C": "git link <remote>",
      "D": "git set-upstream"
    },
    "answer": "A"
  },
  {
    "question": "True or False: In the Gitflow model, the master branch always contains production-ready code.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command shows a list of all remote repositories currently linked to your project?",
    "options": {
      "A": "git remote -v",
      "B": "git remote list",
      "C": "git show remotes",
      "D": "git config remotes"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git fetch updates your working directory files with the latest code from the remote.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO commands are essentially combined when you run git pull?",
    "options": {
      "A": "git fetch",
      "B": "git merge",
      "C": "git push",
      "D": "git checkout"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: git remote prune origin deletes local references to remote branches that have been deleted on the server.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does the -f flag do in git push -f?",
    "options": {
      "A": "It 'Fast-forwards' the merge.",
      "B": "It 'Forces' the push, potentially overwriting history on the remote.",
      "C": "It 'Fixes' broken commits.",
      "D": "It 'Filters' the files being pushed."
    },
    "answer": "B"
  },
  {
    "question": "True or False: You can have multiple remotes named origin in the same local repository.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO protocols does Git primarily use for remote communication?",
    "options": {
      "A": "HTTPS",
      "B": "SSH",
      "C": "FTP",
      "D": "SMTP"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: git clone --depth 1 creates a 'shallow' clone with only the latest commit history.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command adds a new remote named upstream?",
    "options": {
      "A": "git remote add upstream <url>",
      "B": "git remote new upstream <url>",
      "C": "git remote set-url upstream <url>",
      "D": "git config upstream <url>"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git ls-remote allows you to see the references on a remote repository without cloning it.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to save your uncommitted changes to a temporary storage area?",
    "options": {
      "A": "git stash",
      "B": "git save",
      "C": "git pause",
      "D": "git cache"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git stash pop applies the stashed changes and keeps the stash in the list.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO commands apply stashed changes back to your working directory?",
    "options": {
      "A": "git stash apply",
      "B": "git stash pop",
      "C": "git stash push",
      "D": "git stash show"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: git stash list shows all the stashes you have currently saved.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command allows you to view the contents of the last stash without applying it?",
    "options": {
      "A": "git stash show -p",
      "B": "git stash list",
      "C": "git stash view",
      "D": "git stash diff"
    },
    "answer": "A"
  },
  {
    "question": "True or False: You can stash only specific files rather than all changes.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO commands are used to 'undo' a commit?",
    "options": {
      "A": "git reset",
      "B": "git revert",
      "C": "git remove",
      "D": "git delete"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: git revert creates a new commit that does the exact opposite of a previous commit.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which flag in git reset keeps your changes in the working directory but removes them from the staging area?",
    "options": {
      "A": "--soft",
      "B": "--mixed",
      "C": "--hard",
      "D": "--keep"
    },
    "answer": "B"
  },
  {
    "question": "True or False: git reset --hard is safe and never causes data loss.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which command shows who modified each line of a file and in which commit?",
    "options": {
      "A": "git blame",
      "B": "git who",
      "C": "git trace",
      "D": "git log -p"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git log --oneline shows each commit on a single line for a compact view.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO flags can be used to filter the git log?",
    "options": {
      "A": "--author",
      "B": "--since",
      "C": "--who",
      "D": "--time"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: git show displays both the commit message and the actual code diff of a specific commit.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the HEAD in Git?",
    "options": {
      "A": "The first commit of the repository.",
      "B": "A pointer to the current branch/commit you are working on.",
      "C": "The URL of the remote server.",
      "D": "The master branch."
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to combine changes from one branch into another?",
    "options": {
      "A": "git merge",
      "B": "git combine",
      "C": "git link",
      "D": "git attach"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git rebase results in a cleaner, linear project history compared to git merge.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO commands are used to resolve a merge conflict?",
    "options": {
      "A": "git add <resolved_file>",
      "B": "git commit",
      "C": "git resolve",
      "D": "git fix"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: You should always rebase branches that have already been pushed to a public repository.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does git merge --abort do?",
    "options": {
      "A": "It deletes the branch.",
      "B": "It stops the merge process and returns the branch to the pre-merge state.",
      "C": "It force-completes the merge by ignoring conflicts.",
      "D": "It pushes the conflicts to the server."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Squash' commit combines all commits from a feature branch into a single commit.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are valid states for a file in Git?",
    "options": {
      "A": "Staged",
      "B": "Modified",
      "C": "Archived",
      "D": "Pending"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Git can automatically merge two branches if they modified different lines of the same file.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command allows you to pick a single specific commit from one branch and apply it to another?",
    "options": {
      "A": "git cherry-pick",
      "B": "git pick",
      "C": "git select",
      "D": "git commit-copy"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git diff --staged shows the changes between your staging area and your last commit.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Where does Git store all its metadata and object database?",
    "options": {
      "A": "In the .git folder.",
      "B": "In the bin folder.",
      "C": "In the cloud.",
      "D": "In the registry."
    },
    "answer": "A"
  },
  {
    "question": "True or False: Git uses the SHA-1 algorithm to generate unique IDs for commits.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are types of objects Git stores?",
    "options": {
      "A": "Blobs (files)",
      "B": "Trees (directories)",
      "C": "Tables",
      "D": "Links"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: git gc stands for 'Garbage Collect' and helps optimize the repository.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to see the history of all actions taken, including deleted commits?",
    "options": {
      "A": "git reflog",
      "B": "git action-log",
      "C": "git history --all",
      "D": "git log --hidden"
    },
    "answer": "A"
  },
  {
    "question": "True or False: An 'Annotated Tag' contains a message, date, and the name of the person who created it.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command creates a lightweight tag named v1.0?",
    "options": {
      "A": "git tag v1.0",
      "B": "git create tag v1.0",
      "C": "git mark v1.0",
      "D": "git release v1.0"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git help <command> opens the manual page for that specific command.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO files are commonly found in a repository to help developers?",
    "options": {
      "A": "README.md",
      "B": ".gitignore",
      "C": "LICENSE.txt",
      "D": "git.exe"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: You should write commit messages in the present imperative tense (e.g., 'Fix bug').",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to remove a file from the working directory and the index?",
    "options": {
      "A": "git rm",
      "B": "git delete",
      "C": "git remove",
      "D": "git clear"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git rm --cached <file> removes the file from Git tracking but keeps the physical file on disk.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are used to identify a commit?",
    "options": {
      "A": "SHA-1 Hash",
      "B": "Tag name",
      "C": "File name",
      "D": "Branch color"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A 'Bare Repository' is a repository that doesn't have a working directory.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command allows you to change the commit message of the most recent commit?",
    "options": {
      "A": "git commit --amend",
      "B": "git commit --fix",
      "C": "git commit --edit",
      "D": "git commit --update"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git config --list shows all the configuration settings currently active.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command checks the integrity of the Git database?",
    "options": {
      "A": "git fsck",
      "B": "git check",
      "C": "git verify",
      "D": "git status"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git bisect uses binary search to find the specific commit that introduced a bug.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are valid merge conflict markers?",
    "options": {
      "A": "<<<<<<<",
      "B": ">>>>>>>",
      "C": "#######",
      "D": "*******"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Git can handle line ending differences between Windows and Linux automatically.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command shows the manual for Git in the terminal?",
    "options": {
      "A": "git help",
      "B": "man git",
      "C": "git info",
      "D": "git doc"
    },
    "answer": "A"
  },
  {
    "question": "True or False: You can only have one .gitignore file per repository.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to clean untracked files from the working tree?",
    "options": {
      "A": "git clean",
      "B": "git scrub",
      "C": "git clear",
      "D": "git purge"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git clean -f is required to actually delete the files.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command shows a summary of all local and remote branches?",
    "options": {
      "A": "git branch -a",
      "B": "git list --all",
      "C": "git show branches",
      "D": "git remote show"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git checkout - switches you to the previous branch you were on.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO commands relate to working with submodules?",
    "options": {
      "A": "git submodule add",
      "B": "git submodule update",
      "C": "git link-project",
      "D": "git attach-repo"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Each commit in Git contains a snapshot of the entire project structure.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does git diff with no arguments compare?",
    "options": {
      "A": "Working directory vs Staging Area.",
      "B": "Staging Area vs Last Commit.",
      "C": "Working directory vs Last Commit.",
      "D": "Local branch vs Remote branch."
    },
    "answer": "A"
  },
  {
    "question": "True or False: git log -p shows the patch (diff) introduced in each commit.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to see all the configuration levels (system, global, local)?",
    "options": {
      "A": "git config --list --show-origin",
      "B": "git config --all",
      "C": "git show config",
      "D": "git config --levels"
    },
    "answer": "A"
  },
  {
    "question": "True or False: Git is a decentralized version control system.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command allows you to edit the global Git config file?",
    "options": {
      "A": "git config --global --edit",
      "B": "git edit-config",
      "C": "git set --global",
      "D": "git global-config"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git archive can be used to create a zip or tar file of your repository.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the default name for the primary branch in newer Git repositories?",
    "options": {
      "A": "main",
      "B": "master",
      "C": "root",
      "D": "trunk"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git show-branch shows the commits for each branch and their relationship.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are standard Git commit message sections?",
    "options": {
      "A": "Subject Line",
      "B": "Body",
      "C": "Version Number",
      "D": "Author Bio"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Commits in Git are immutable; you cannot change a commit once it is created.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to verify the GPG signature of a commit?",
    "options": {
      "A": "git verify-commit",
      "B": "git check-sign",
      "C": "git show --show-signature",
      "D": "git log --verify"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git stash drop deletes a specific stash entry.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command applies a stash without removing it from the stash list?",
    "options": {
      "A": "git stash apply",
      "B": "git stash pop",
      "C": "git stash show",
      "D": "git stash keep"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git remote set-url origin <new_url> is used to change the URL of an existing remote.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are used to create a new branch?",
    "options": {
      "A": "git branch <name>",
      "B": "git checkout -b <name>",
      "C": "git new-branch <name>",
      "D": "git switch -c <name>"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Git uses a directed acyclic graph (DAG) to represent history.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command shows the SHA-1 of the current commit?",
    "options": {
      "A": "git rev-parse HEAD",
      "B": "git show --id",
      "C": "git get-id",
      "D": "git head-hash"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git push --tags is required to push your local tags to the remote server.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command displays the status of the repository in a short format?",
    "options": {
      "A": "git status -s",
      "B": "git status --short",
      "C": "git status --compact",
      "D": "git show status"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git diff --cached is the same as git diff --staged.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO commands show the differences between commits?",
    "options": {
      "A": "git diff",
      "B": "git show",
      "C": "git log -p",
      "D": "git status"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A Git 'Hook' is a script that runs automatically when a certain event happens.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to remove a remote from your repository?",
    "options": {
      "A": "git remote remove <name>",
      "B": "git remote delete <name>",
      "C": "git remote rm <name>",
      "D": "git remote clear <name>"
    },
    "answer": "A"
  },
  {
    "question": "True or False: git checkout <commit_hash> <file> restores a single file from a previous commit.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command lists all configured aliases?",
    "options": {
      "A": "git config --get-regexp alias",
      "B": "git alias --list",
      "C": "git show-aliases",
      "D": "git config --aliases"
    },
    "answer": "A"
  },
  {
    "question": "True or False: Git can be used for version control of binary files like images.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command summarizes the commit history by author?",
    "options": {
      "A": "git shortlog",
      "B": "git log --author-summary",
      "C": "git who-did-what",
      "D": "git stats"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary purpose of the Virtual DOM in React?",
    "options": {
      "A": "To directly manipulate the browser's DOM for speed.",
      "B": "To create a lightweight copy of the real DOM to improve performance via efficient syncing.",
      "C": "To store data in a local database.",
      "D": "To handle server-side routing."
    },
    "answer": "B"
  },
  {
    "question": "Which hook is used to manage side effects in a functional component?",
    "options": {
      "A": "useState",
      "B": "useContext",
      "C": "useEffect",
      "D": "useReducer"
    },
    "answer": "C"
  },
  {
    "question": "True or False: React components must start with a capital letter.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO valid ways to pass data from a parent to a child component:",
    "options": {
      "A": "Props",
      "B": "Context API",
      "C": "Redux Dispatch",
      "D": "Static Variables"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What does JSX stand for?",
    "options": {
      "A": "JavaScript XML",
      "B": "Java Syntax Extension",
      "C": "JSON X-platform",
      "D": "JavaScript Xerography"
    },
    "answer": "A"
  },
  {
    "question": "True or False: 'State' in React is immutable and should not be modified directly.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to create a new React app using the official CLI?",
    "options": {
      "A": "npm install react",
      "B": "npx create-react-app my-app",
      "C": "git init react-app",
      "D": "react-new-project"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO built-in React hooks:",
    "options": {
      "A": "useFetch",
      "B": "useMemo",
      "C": "useCallback",
      "D": "useAsync"
    },
    "answer": ["B", "C"]
  },
  {
    "question": "True or False: A React component can return multiple root elements without using a Fragment.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'key' prop in a list of elements?",
    "options": {
      "A": "To style the elements uniquely.",
      "B": "To help React identify which items have changed, been added, or removed.",
      "C": "To set a password for the component.",
      "D": "To link to an external database ID."
    },
    "answer": "B"
  },
  {
    "question": "Which hook would you use to reference a DOM element directly?",
    "options": {
      "A": "useRef",
      "B": "useDOM",
      "C": "usePointer",
      "D": "useState"
    },
    "answer": "A"
  },
  {
    "question": "True or False: Functional components in React can use state using the useState hook.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO libraries commonly used for Routing in React:",
    "options": {
      "A": "React Router",
      "B": "TanStack Router",
      "C": "Redux Thunk",
      "D": "Axios"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Prop Drilling'?",
    "options": {
      "A": "Optimizing props for performance.",
      "B": "The process of passing data through many layers of components to reach a deeply nested child.",
      "C": "Deleting unused props.",
      "D": "Validating props with TypeScript."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The useMemo hook is used to cache the results of expensive calculations.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the default port for a local development server in Create React App?",
    "options": {
      "A": "8080",
      "B": "5000",
      "C": "3000",
      "D": "4200"
    },
    "answer": "C"
  },
  {
    "question": "Identify TWO states of a React component lifecycle (Conceptual):",
    "options": {
      "A": "Mounting",
      "B": "Unmounting",
      "C": "Downloading",
      "D": "Compiling"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Hooks can be called inside loops or conditions.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Strict Mode' component do in React?",
    "options": {
      "A": "Increases app performance.",
      "B": "Highlights potential problems in an application during development.",
      "C": "Forces the app to run in dark mode.",
      "D": "Prevents the use of any third-party libraries."
    },
    "answer": "B"
  },
  {
    "question": "Which property is used in JSX to set a CSS class?",
    "options": {
      "A": "class",
      "B": "className",
      "C": "styleClass",
      "D": "css"
    },
    "answer": "B"
  },
  {
    "question": "True or False: React follows a Unidirectional (one-way) data flow.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a 'Higher-Order Component' (HOC)?",
    "options": {
      "A": "A component that sits at the top of the tree.",
      "B": "A function that takes a component and returns a new component.",
      "C": "A component with a high Z-index.",
      "D": "A class-based component."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO ways to style React components:",
    "options": {
      "A": "CSS Modules",
      "B": "Styled Components",
      "C": "Inline SQL",
      "D": "HTML Attributes"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: The useEffect hook cleanup function runs before the component unmounts.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of 'React Fragments'?",
    "options": {
      "A": "To split the code into multiple files.",
      "B": "To group a list of children without adding extra nodes to the DOM.",
      "C": "To handle image compression.",
      "D": "To speed up API calls."
    },
    "answer": "B"
  },
  {
    "question": "Which hook is used to share data across the component tree without prop drilling?",
    "options": {
      "A": "useState",
      "B": "useContext",
      "C": "useMemo",
      "D": "useShare"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Portals provide a way to render children into a DOM node that exists outside the hierarchy of the parent component.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO advantages of using Vite over Create React App (CRA):",
    "options": {
      "A": "Faster cold server start.",
      "B": "Instant Hot Module Replacement (HMR).",
      "C": "Older browser support by default.",
      "D": "Automatic code documentation."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is 'Lazy Loading' in React?",
    "options": {
      "A": "Delaying the state update.",
      "B": "Loading components only when they are needed to reduce initial bundle size.",
      "C": "A bug where components load slowly.",
      "D": "Automatically refreshing the page."
    },
    "answer": "B"
  },
  {
    "question": "True or False: React can be used for both web and mobile application development (React Native).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which function is used to change state in a class component?",
    "options": {
      "A": "this.updateState()",
      "B": "this.setState()",
      "C": "this.changeState()",
      "D": "this.state = {}"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO features of 'Controlled Components':",
    "options": {
      "A": "The form data is handled by the React component state.",
      "B": "React has the 'single source of truth' for the input value.",
      "C": "The data is stored directly in the DOM.",
      "D": "It requires a physical controller device."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Props are read-only.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of the useReducer hook?",
    "options": {
      "A": "To compress JSON data.",
      "B": "To handle complex state logic involving multiple sub-values.",
      "C": "To reduce the number of components.",
      "D": "To delete old state data."
    },
    "answer": "B"
  },
  {
    "question": "Which method is called after a class component is rendered for the first time?",
    "options": {
      "A": "componentWillMount",
      "B": "componentDidMount",
      "C": "componentWillUpdate",
      "D": "componentDidUpdate"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Conditional rendering in React can be done using ternary operators.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common state management libraries for React:",
    "options": {
      "A": "Redux",
      "B": "Zustand",
      "C": "Bootstrap",
      "D": "jQuery"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What does the 'dependency array' in useEffect control?",
    "options": {
      "A": "The list of npm packages needed.",
      "B": "When the effect should re-run based on variable changes.",
      "C": "The order of CSS files.",
      "D": "The database connection string."
    },
    "answer": "B"
  },
  {
    "question": "True or False: React DevTools is a browser extension used to inspect the React component hierarchy.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Shadow DOM' in relation to React?",
    "options": {
      "A": "It is exactly the same as Virtual DOM.",
      "B": "It is a browser technology used for encapsulation, separate from React's Virtual DOM.",
      "C": "It is a deprecated feature of React.",
      "D": "It is used for backend rendering."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO rules of Hooks:",
    "options": {
      "A": "Only call hooks at the top level.",
      "B": "Only call hooks from React function components.",
      "C": "Always call hooks inside try/catch blocks.",
      "D": "Hooks must return a Promise."
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: A component re-renders whenever its props or state change.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which hook is used for performance optimization by memoizing a whole function?",
    "options": {
      "A": "useMemo",
      "B": "useCallback",
      "C": "useEffect",
      "D": "useFunction"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'children' prop?",
    "options": {
      "A": "To count the number of components.",
      "B": "To pass elements or components as data to other components.",
      "C": "To link a parent to a child in the database.",
      "D": "To handle form validation."
    },
    "answer": "B"
  },
  {
    "question": "True or False: Every React component must return a single JSX element (or null).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which hook is used to access the current URL location in React Router?",
    "options": {
      "A": "useParams",
      "B": "useLocation",
      "C": "useHistory",
      "D": "useRoute"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO common ways to handle API calls in React:",
    "options": {
      "A": "fetch API",
      "B": "Axios library",
      "C": "SQL Queries",
      "D": "Direct file reading"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: useRef values do not trigger a re-render when changed.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the role of a 'Store' in Redux?",
    "options": {
      "A": "To save the app's images.",
      "B": "To hold the entire state tree of your application.",
      "C": "To manage API endpoints.",
      "D": "To host the production build."
    },
    "answer": "B"
  },
  {
    "question": "Which method is used in React 18 to create a root and render a component?",
    "options": {
      "A": "ReactDOM.render()",
      "B": "createRoot()",
      "C": "renderRoot()",
      "D": "App.render()"
    },
    "answer": "B"
  }
]
    
    
      

def remove_duplicates(questions):
    seen = set()
    unique = []

    for q in questions:
        if q["question"] not in seen:
            seen.add(q["question"])
            unique.append(q)

    return unique


def generate_pdf(skill_name, questions):
    doc = SimpleDocTemplate(
        f"{skill_name}_Question_Bank.pdf",
        pagesize=A4
    )

    elements = []
    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    elements.append(Paragraph(f"{skill_name} Question Bank ({len(questions)} Questions)", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    for i, q in enumerate(questions, 1):
        elements.append(Paragraph(f"{i}. {q['question']}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))

        for key, value in q["options"].items():
            elements.append(Paragraph(f"{key}) {value}", normal_style))
            elements.append(Spacer(1, 0.05 * inch))

        elements.append(Paragraph(f"<b>Answer:</b> {q['answer']}", normal_style))
        elements.append(Spacer(1, 0.3 * inch))

    doc.build(elements)
    print(f"✅ PDF Generated with {len(questions)} UNIQUE questions only.")


if __name__ == "__main__":
    skill = "Git"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
