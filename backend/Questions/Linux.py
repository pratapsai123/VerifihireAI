from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "Which command is used to display the current working directory?",
    "options": {
      "A": "dir",
      "B": "pwd",
      "C": "cd",
      "D": "ls"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Linux is a case-sensitive operating system.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO characters represent the home directory of the current user?",
    "options": {
      "A": "~",
      "B": "$HOME",
      "C": "/",
      "D": ".."
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The /etc directory typically contains binary executable files.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to create a new directory?",
    "options": {
      "A": "touch",
      "B": "mkdir",
      "C": "newdir",
      "D": "create"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO commands used to list files in a directory:",
    "options": {
      "A": "ls",
      "B": "dir",
      "C": "list",
      "D": "show"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: In Linux, everything is treated as a file, including hardware devices.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which directory contains system log files?",
    "options": {
      "A": "/bin",
      "B": "/var/log",
      "C": "/lib",
      "D": "/usr"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to delete an empty directory?",
    "options": {
      "A": "del",
      "B": "rmdir",
      "C": "erase",
      "D": "remove"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The root user has the UID (User ID) of 0.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What command is used to change file permissions?",
    "options": {
      "A": "chown",
      "B": "chmod",
      "C": "chgrp",
      "D": "perm"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The permission rwxr-xr-x corresponds to the octal value 755.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO symbolic modes used with chmod:",
    "options": {
      "A": "u+x",
      "B": "g-w",
      "C": "755",
      "D": "octal"
    },
    "answer": "A, B"
  },
  {
    "question": "Which command provides a real-time view of running processes?",
    "options": {
      "A": "ps",
      "B": "top",
      "C": "lsprc",
      "D": "cron"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The kill -9 command sends a SIGKILL signal to immediately terminate a process.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO ways to run a process in the background:",
    "options": {
      "A": "Adding & at the end",
      "B": "Using bg command after Ctrl+Z",
      "C": "Using stop command",
      "D": "Using fg command"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the PID of the first process started by the Linux kernel?",
    "options": {
      "A": "0",
      "B": "1",
      "C": "100",
      "D": "-1"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Zombie' process is a process that has completed execution but still has an entry in the process table.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to schedule tasks to run at specific intervals?",
    "options": {
      "A": "at",
      "B": "crontab",
      "C": "schedule",
      "D": "taskmgr"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO commands used to terminate a process by its name rather than its PID:",
    "options": {
      "A": "pkill",
      "B": "killall",
      "C": "stop-name",
      "D": "terminate"
    },
    "answer": "A, B"
  },
  {
    "question": "Which command is used to check the IP address of network interfaces on modern systems?",
    "options": {
      "A": "ip addr",
      "B": "ifconfig",
      "C": "netstat",
      "D": "route"
    },
    "answer": "A"
  },
  {
    "question": "True or False: The /etc/hosts file maps IP addresses to hostnames locally.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO commands used to download files from the internet via terminal:",
    "options": {
      "A": "wget",
      "B": "curl",
      "C": "get",
      "D": "download"
    },
    "answer": "A, B"
  },
  {
    "question": "Which command is used to search for a string within a file?",
    "options": {
      "A": "find",
      "B": "grep",
      "C": "locate",
      "D": "search"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The echo command is used to print text or variables to the terminal.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the standard 'Shebang' line for a Bash script?",
    "options": {
      "A": "!/bin/bash",
      "B": "#!/bin/bash",
      "C": "#bash",
      "D": "//bin/bash"
    },
    "answer": "B"
  },
  {
    "question": "True or False: In a script, the variable $1 represents the first command-line argument passed to the script.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO ways to make a script file named myscript.sh executable:",
    "options": {
      "A": "chmod +x myscript.sh",
      "B": "chmod 755 myscript.sh",
      "C": "chown +x myscript.sh",
      "D": "bash myscript.sh"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The command export VARNAME=value makes the variable available to child processes and subshells.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to read input from a user during script execution?",
    "options": {
      "A": "input",
      "B": "get",
      "C": "read",
      "D": "scan"
    },
    "answer": "C"
  },
  {
    "question": "Which TWO operators are used for numeric comparison in a standard Bash [ ] if statement?",
    "options": {
      "A": "-eq",
      "B": "-gt",
      "C": "==",
      "D": ">"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The special variable $? stores the exit status of the last executed command, where 0 indicates success.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does the 2> operator do in the Linux shell?",
    "options": {
      "A": "Redirects standard output (stdout)",
      "B": "Redirects standard error (stderr)",
      "C": "Appends to a file",
      "D": "Pipes to another command"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The file /etc/resolv.conf is used to configure DNS nameserver addresses.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO tools used to check if a specific port is open on a remote server:",
    "options": {
      "A": "telnet",
      "B": "nc (netcat)",
      "C": "ping",
      "D": "traceroute"
    },
    "answer": "A, B"
  },
  {
    "question": "Which protocol does the 'ping' command use to check network connectivity?",
    "options": {
      "A": "TCP",
      "B": "UDP",
      "C": "ICMP",
      "D": "HTTP"
    },
    "answer": "C"
  },
  {
    "question": "True or False: The mount command is used to attach a filesystem to the system hierarchy.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common native Linux filesystems:",
    "options": {
      "A": "ext4",
      "B": "xfs",
      "C": "NTFS",
      "D": "HFS"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The /etc/fstab file contains information about which filesystems are mounted automatically at boot.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to safely unmount a filesystem?",
    "options": {
      "A": "unmount",
      "B": "umount",
      "C": "remove",
      "D": "detach"
    },
    "answer": "B"
  },
  {
    "question": "True or False: systemctl is the modern command used to manage systemd services.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command shows the logs for a specific service managed by systemd?",
    "options": {
      "A": "cat /var/log/syslog",
      "B": "journalctl -u service_name",
      "C": "logview",
      "D": "service status"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Swap space is used as 'overflow' memory when the physical RAM is full.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to check and repair a Linux filesystem?",
    "options": {
      "A": "fsck",
      "B": "repair",
      "C": "checkdisk",
      "D": "mkfs"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO ways to view the current system time and date:",
    "options": {
      "A": "date",
      "B": "timedatectl",
      "C": "clock",
      "D": "time"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The /boot directory contains the Linux kernel and bootloader files.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to securely copy files between hosts?",
    "options": {
      "A": "cp",
      "B": "scp",
      "C": "ftp",
      "D": "rcp"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Soft Link' can point to a directory, whereas a 'Hard Link' cannot.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to reload the systemd manager configuration after editing a service file?",
    "options": {
      "A": "systemctl daemon-reload",
      "B": "service reload",
      "C": "reload-systemd",
      "D": "init 6"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common methods for remote file transfer that use encryption:",
    "options": {
      "A": "scp",
      "B": "sftp",
      "C": "rdp",
      "D": "telnet"
    },
    "answer": "A, B"
  },
  {
    "question": "Which command is used to display the current system uptime and load average?",
    "options": {
      "A": "time",
      "B": "uptime",
      "C": "load",
      "D": "top -l"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The /tmp directory is used for storing temporary files that are often cleared upon reboot.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO sections are modified when using 'chown user:group filename'?",
    "options": {
      "A": "Owner",
      "B": "Group",
      "C": "Permissions",
      "D": "Timestamp"
    },
    "answer": "A, B"
  },
  {
    "question": "What does the 's' in a file permission (SUID) allow?",
    "options": {
      "A": "The file to be shared.",
      "B": "The file to run with the permissions of the file owner.",
      "C": "The file to be hidden.",
      "D": "The file to be encrypted."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The umask command determines the default permissions for newly created files.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which numerical value represents 'execute' permission in Linux?",
    "options": {
      "A": "1",
      "B": "2",
      "C": "4",
      "D": "7"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO ways to represent the 'write' permission:",
    "options": {
      "A": "The letter w",
      "B": "The number 2",
      "C": "The letter x",
      "D": "The number 4"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: If a file has permissions 000, even the root user cannot read it without changing permissions first.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'Sticky Bit' permission on a directory do?",
    "options": {
      "A": "Makes the directory invisible.",
      "B": "Prevents users from deleting files they do not own within that directory.",
      "C": "Speeds up file access.",
      "D": "Automatically encrypts new files."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO commands used to view current user identity and groups:",
    "options": {
      "A": "id",
      "B": "whoami",
      "C": "user",
      "D": "showme"
    },
    "answer": "A, B"
  },
  {
    "question": "Which file stores the encrypted passwords for users on a Linux system?",
    "options": {
      "A": "/etc/passwd",
      "B": "/etc/shadow",
      "C": "/etc/config",
      "D": "/etc/secure"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A Symbolic Link (Soft Link) becomes 'broken' if the original source file is deleted.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to find all files owned by a specific user?",
    "options": {
      "A": "ls -user",
      "B": "find / -user username",
      "C": "search -owner username",
      "D": "locate -u username"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO characteristics of a Hard Link:",
    "options": {
      "A": "It has the same Inode number as the original file.",
      "B": "It continues to work even if the original file is moved within the same filesystem.",
      "C": "It can cross different file systems.",
      "D": "It is essentially a shortcut or pointer to a filename."
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The visudo command is the safest way to edit the /etc/sudoers file because it checks for syntax errors.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to add a new user to the system?",
    "options": {
      "A": "useradd",
      "B": "newuser",
      "C": "adduser",
      "D": "Both A and C"
    },
    "answer": "D"
  },
  {
    "question": "True or False: df -h is used to check memory (RAM) usage.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which command displays the amount of free and used memory in the system?",
    "options": {
      "A": "mem",
      "B": "free",
      "C": "ram",
      "D": "df"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO commands used to view the system kernel version:",
    "options": {
      "A": "uname -a",
      "B": "cat /proc/version",
      "C": "kernel -v",
      "D": "ver"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: In the top command, the 'RES' column represents the non-swapped physical memory a task is using.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to display the kernel ring buffer or system boot messages?",
    "options": {
      "A": "bootlog",
      "B": "dmesg",
      "C": "klog",
      "D": "syslog"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The lsof command is used to list all open files and the processes that opened them.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command displays the user's manual for the system's partitions and mount points?",
    "options": {
      "A": "lsblk",
      "B": "fdisk -l",
      "C": "mount -list",
      "D": "Both A and B"
    },
    "answer": "D"
  },
  {
    "question": "True or False: The sar command (System Activity Reporter) is used to collect and report system activity information.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO directories usually mounted on their own partitions for better stability:",
    "options": {
      "A": "/home",
      "B": "/var",
      "C": "/bin",
      "D": "/etc"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The command pstree shows running processes as a tree, displaying parent-child relationships visually.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which file system is commonly used as the default for modern Linux distributions like Ubuntu or Fedora?",
    "options": {
      "A": "NTFS",
      "B": "ext4",
      "C": "FAT32",
      "D": "HFS+"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Daemon' is a background process that handles system-level tasks and usually ends with 'd' (e.g., sshd).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command allows you to view the hierarchy of the PCI buses and devices in the system?",
    "options": {
      "A": "lspci",
      "B": "lsusb",
      "C": "lsdev",
      "D": "businfo"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to display or modify the system's routing table?",
    "options": {
      "A": "ip route",
      "B": "route",
      "C": "netstat -r",
      "D": "All of the above"
    },
    "answer": "D"
  },
  {
    "question": "True or False: ssh stands for Secure Shell and uses port 22 by default.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to securely copy files between hosts over a network?",
    "options": {
      "A": "cp",
      "B": "scp",
      "C": "ftp",
      "D": "rcp"
    },
    "answer": "B"
  },
  {
    "question": "True or False: grep -i makes a text search case-insensitive.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO text editors commonly found in the Linux terminal:",
    "options": {
      "A": "vi",
      "B": "nano",
      "C": "notepad",
      "D": "word"
    },
    "answer": "A, B"
  },
  {
    "question": "Which command is used to compress files into a .tar.gz archive?",
    "options": {
      "A": "zip",
      "B": "tar",
      "C": "gzip",
      "D": "compress"
    },
    "answer": "B"
  },
  {
    "question": "True or False: tail -f is used to follow a log file in real-time as it grows.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are valid package managers commonly used in Linux?",
    "options": {
      "A": "apt",
      "B": "yum",
      "C": "install-pkg",
      "D": "exe"
    },
    "answer": "A, B"
  },
  {
    "question": "What is a 'Shebang' in a Linux script?",
    "options": {
      "A": "A comment at the end of a script.",
      "B": "The first line (e.g., #!/bin/bash) telling the OS which interpreter to use.",
      "C": "A specific error message.",
      "D": "A hidden file."
    },
    "answer": "B"
  },
  {
    "question": "True or False: /dev/null is often called the 'black hole' because any data sent there disappears.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to display disk usage of files and directories specifically?",
    "options": {
      "A": "df",
      "B": "du",
      "C": "dd",
      "D": "ds"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The alias command allows you to create a shortcut for a long or frequent command.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to sort the lines of text files alphabetically or numerically?",
    "options": {
      "A": "order",
      "B": "sort",
      "C": "arrange",
      "D": "organize"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The rsync command is highly efficient because it only transfers the differences between files.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to check the health of a hard drive using S.M.A.R.T. data?",
    "options": {
      "A": "smartctl",
      "B": "diskcheck",
      "C": "hdd-health",
      "D": "fsck"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary function of the 'nc' (Netcat) command?",
    "options": {
      "A": "Reads and writes data across network connections using TCP or UDP.",
      "B": "Cleans the network card cache.",
      "C": "Checks the computer's motherboard name.",
      "D": "Installs network drivers."
    },
    "answer": "A"
  },
  {
    "question": "True or False: The strace command is used to trace system calls and signals for debugging.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to see the UUIDs (Universally Unique Identifiers) of all partitions?",
    "options": {
      "A": "blkid",
      "B": "lsblk -f",
      "C": "show-uuid",
      "D": "Both A and B"
    },
    "answer": "D"
  },
  {
    "question": "True or False: TCP Wrappers use /etc/hosts.allow and /etc/hosts.deny to control network access.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO types of Unix/Linux Shells:",
    "options": {
      "A": "Bash",
      "B": "Zsh",
      "C": "C-Plus",
      "D": "HyperShell"
    },
    "answer": "A, B"
  },
  {
    "question": "Which command is used to find files that have been modified within the last 24 hours?",
    "options": {
      "A": "find . -mtime 0",
      "B": "ls -recent",
      "C": "search -new",
      "D": "modified-list"
    },
    "answer": "A"
  },
  {
    "question": "True or False: The chattr command is used to change file attributes, such as making a file immutable.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO common methods for remote file transfer:",
    "options": {
      "A": "scp",
      "B": "sftp",
      "C": "rdp",
      "D": "telnet"
    },
    "answer": "A, B"
  },
  {
    "question": "Which command provides a real-time view of running processes with CPU and Memory usage?",
    "options": {
      "A": "ps",
      "B": "top",
      "C": "lsprc",
      "D": "cron"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Linux uses a 'Inverted Tree' structure for its filesystem, starting from the root (/).",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of the 'chmod' command?",
    "options": {
      "A": "Change file owner",
      "B": "Change file access permissions",
      "C": "Change file group",
      "D": "Change file name"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to display or modify the system's network interface configuration, such as setting an IP address?",
    "options": {
      "A": "ip addr",
      "B": "ifconfig",
      "C": "netstat",
      "D": "Both A and B"
    },
    "answer": "D"
  },
  {
    "question": "True or False: The 'traceroute' command uses ICMP or UDP packets with increasing TTL values to map the path to a destination.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO commands used to view current listening ports and active network connections on a system:",
    "options": {
      "A": "ss",
      "B": "netstat",
      "C": "ip link",
      "D": "hostname"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the purpose of the '/etc/resolv.conf' file in a Linux system?",
    "options": {
      "A": "To store local hostnames.",
      "B": "To configure DNS nameserver addresses for name resolution.",
      "C": "To set the system's IP address.",
      "D": "To manage firewall rules."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'dig' command (Domain Information Groper) is a modern tool for querying DNS name servers.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO operators are used to redirect Standard Error (stderr) in the Bash shell?",
    "options": {
      "A": "2>",
      "B": "2>>",
      "C": "1>",
      "D": "&>"
    },
    "answer": "A, B"
  },
  {
    "question": "What does the 'nice' command do in Linux process management?",
    "options": {
      "A": "It kills a process politely.",
      "B": "It launches a process with a specific scheduling priority.",
      "C": "It cleans up temporary files created by a process.",
      "D": "It displays a friendly message to the user."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Hard Link' cannot be created for a directory or across different filesystems.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to display the amount of free and used memory (RAM) and swap space in the system?",
    "options": {
      "A": "df",
      "B": "free",
      "C": "meminfo",
      "D": "top"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO ways to view the contents of a text file line-by-line without opening a full editor:",
    "options": {
      "A": "less",
      "B": "more",
      "C": "touch",
      "D": "mkdir"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the function of the 'umask' value in a Linux environment?",
    "options": {
      "A": "It sets the maximum number of open files.",
      "B": "It acts as a mask to determine default permissions for newly created files and directories.",
      "C": "It encrypts the user's password.",
      "D": "It masks the IP address of the user."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'set -e' command in a Bash script causes the script to exit immediately if any command exits with a non-zero status.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO symbols are used for 'logical AND' and 'logical OR' respectively between commands in a shell script?",
    "options": {
      "A": "&&",
      "B": "||",
      "C": "&",
      "D": "|"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the purpose of the 'sticky bit' on a directory like '/tmp'?",
    "options": {
      "A": "To make the directory permanent and undeletable.",
      "B": "To ensure that only the owner of a file (or root) can delete or rename it within that directory.",
      "C": "To keep the directory in the CPU cache.",
      "D": "To stick files together for compression."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'LVM' (Logical Volume Manager) allows for the resizing of partitions while the filesystem is still mounted.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to display the most recent system login attempts and session history?",
    "options": {
      "A": "history",
      "B": "last",
      "C": "who",
      "D": "login-log"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO types of process signals used to stop or kill a process in Linux:",
    "options": {
      "A": "SIGTERM (15)",
      "B": "SIGKILL (9)",
      "C": "SIGSTOP",
      "D": "SIGDEAD"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the role of the 'init' or 'systemd' process in Linux?",
    "options": {
      "A": "It is the first process (PID 1) and the parent of all other processes.",
      "B": "It manages the graphical user interface.",
      "C": "It is responsible for hardware driver installation.",
      "D": "It encrypts the hard drive."
    },
    "answer": "A"
  },
  {
    "question": "True or False: The 'crontab -l' command is used to list the scheduled tasks for the current user.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to find the full path of a command's binary file?",
    "options": {
      "A": "find",
      "B": "which",
      "C": "whereis",
      "D": "locate"
    },
    "answer": "B"
  },
  {
    "question": "Which file contains the list of all filesystems that should be automatically mounted at system startup?",
    "options": {
      "A": "/etc/mtab",
      "B": "/etc/fstab",
      "C": "/proc/mounts",
      "D": "/etc/filesystems"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'load average' in Linux represents the number of processes in a runnable or uninterruptible state over a specific period.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO commands used to view or manage kernel modules at runtime:",
    "options": {
      "A": "lsmod",
      "B": "modprobe",
      "C": "kerninit",
      "D": "sysctl"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the purpose of the 'Swap' partition in a Linux system?",
    "options": {
      "A": "To store encrypted user data.",
      "B": "To act as virtual memory on the disk when physical RAM is exhausted.",
      "C": "To swap files between different users.",
      "D": "To speed up boot times."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'chmod 777' command is considered a security best practice for shared directories.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO files are typically used by 'TCP Wrappers' to allow or deny network services to specific hosts?",
    "options": {
      "A": "/etc/hosts.allow",
      "B": "/etc/hosts.deny",
      "C": "/etc/network/interfaces",
      "D": "/etc/iptables.conf"
    },
    "answer": "A, B"
  },
  {
    "question": "What does the command 'top -p [PID]' do?",
    "options": {
      "A": "Changes the priority of the process.",
      "B": "Monitors only the specific process ID provided.",
      "C": "Kills the process immediately.",
      "D": "Displays the parent of the process."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'journalctl' command is used to query and display logs from the systemd-journald service.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to display the default gateway and current routing table entries?",
    "options": {
      "A": "ip route show",
      "B": "netstat -r",
      "C": "route -n",
      "D": "All of the above"
    },
    "answer": "D"
  },
  {
    "question": "Identify TWO signals that are commonly sent using the 'kill' command to terminate processes gracefully:",
    "options": {
      "A": "SIGTERM (15)",
      "B": "SIGHUP (1)",
      "C": "SIGKILL (9)",
      "D": "SIGWAIT"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the result of the command 'tail -n 20 access.log'?",
    "options": {
      "A": "Displays the first 20 lines of the file.",
      "B": "Displays the last 20 lines of the file.",
      "C": "Deletes the last 20 lines of the file.",
      "D": "Monitors the last 20 lines in real-time."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Zombie' process consumes CPU cycles but no memory.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are common package management tools used on Debian-based distributions (like Ubuntu)?",
    "options": {
      "A": "apt",
      "B": "dpkg",
      "C": "yum",
      "D": "dnf"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the purpose of the 'chroot' command?",
    "options": {
      "A": "To change the root password.",
      "B": "To change the root directory for a process and its children to a new location.",
      "C": "To check the root partition for errors.",
      "D": "To reboot the system to the root prompt."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'sync' command is used to force write cached data to disk.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO methods to view the real-time load and process activity on a Linux server:",
    "options": {
      "A": "top",
      "B": "htop",
      "C": "ps -ef",
      "D": "df -h"
    },
    "answer": "A, B"
  },
  {
    "question": "What does the 'df -h' command show?",
    "options": {
      "A": "The amount of used and available disk space in human-readable format.",
      "B": "The amount of used and available RAM.",
      "C": "The directory structure hierarchy.",
      "D": "The CPU frequency."
    },
    "answer": "A"
  },
  {
    "question": "True or False: The '/proc' directory is a virtual filesystem that provides a window into the Linux kernel and process information.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to verify the integrity and correct errors on an unmounted filesystem?",
    "options": {
      "A": "fsck",
      "B": "fdisk",
      "C": "mkfs",
      "D": "mount"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO commands that can be used to securely log into a remote Linux server:",
    "options": {
      "A": "ssh",
      "B": "telnet",
      "C": "rlogin",
      "D": "putty (client side)"
    },
    "answer": "A, D"
  },
  {
    "question": "What does the 'uptime' command provide?",
    "options": {
      "A": "Total time since the last reboot.",
      "B": "Number of users logged in.",
      "C": "System load averages.",
      "D": "All of the above."
    },
    "answer": "D"
  },
  {
    "question": "True or False: A 'SIGKILL (9)' signal allows a process to save its state before terminating.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which directory contains the system's static configuration files for bootup and services?",
    "options": {
      "A": "/bin",
      "B": "/etc",
      "C": "/var",
      "D": "/lib"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'lsof' command can be used to find which process is using a specific network port.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO characters are used in a Bash script to signify a comment?",
    "options": {
      "A": "#",
      "B": "//",
      "C": ";",
      "D": "--"
    },
    "answer": "A, C"
  },
  {
    "question": "What is the function of the 'umask 022' command?",
    "options": {
      "A": "Sets default directory permissions to 755.",
      "B": "Sets default file permissions to 644.",
      "C": "Both A and B.",
      "D": "Limits the number of processes per user."
    },
    "answer": "C"
  },
  {
    "question": "True or False: In Linux, a process can have multiple parents but only one child.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to check the available space on the system's memory and swap partitions in real-time?",
    "options": {
      "A": "free -m",
      "B": "vmstat",
      "C": "sar",
      "D": "All of the above"
    },
    "answer": "D"
  },
  {
    "question": "Identify TWO types of Linux links that can point to a file:",
    "options": {
      "A": "Hard Link",
      "B": "Soft (Symbolic) Link",
      "C": "Hyper Link",
      "D": "Static Link"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the primary difference between 'top' and 'htop'?",
    "options": {
      "A": "top is a graphical tool, htop is CLI.",
      "B": "htop provides a more user-friendly, colorized, and interactive interface than top.",
      "C": "top monitors disk usage, htop monitors memory.",
      "D": "There is no functional difference."
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to modify the 'nice' value of a process that is already running?",
    "options": {
      "A": "nice",
      "B": "renice",
      "C": "setpriority",
      "D": "priority"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The /proc/sys directory allows you to modify kernel parameters on the fly without rebooting.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO commands used to view the PCI and USB devices currently connected to the system:",
    "options": {
      "A": "lspci",
      "B": "lsusb",
      "C": "lsdev",
      "D": "lshw"
    },
    "answer": "A, B"
  },
  {
    "question": "What is the purpose of the 'LD_LIBRARY_PATH' environment variable?",
    "options": {
      "A": "To set the path for executable binaries.",
      "B": "To specify additional directories where the loader should search for shared libraries.",
      "C": "To store the location of the Linux kernel.",
      "D": "To list the home directories of all users."
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Hard Link' can point to a file on a different physical disk partition.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to display the shared library dependencies of a specific binary executable?",
    "options": {
      "A": "ldd",
      "B": "ls-lib",
      "C": "objdump",
      "D": "readelf"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO ways to send the output of a command to both a file and the terminal screen simultaneously:",
    "options": {
      "A": "Using the tee command",
      "B": "Using > and & together",
      "C": "Using the multi-output flag",
      "D": "Using | tee -a"
    },
    "answer": "A, D"
  },
  {
    "question": "In a Bash script, what does the 'shift' command do?",
    "options": {
      "A": "It moves the script to a different directory.",
      "B": "It shifts positional parameters ($1, $2, etc.) to the left.",
      "C": "It renames a variable.",
      "D": "It pauses the script for a specific duration."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'setuid' bit on a directory causes new files created within it to inherit the directory's owner.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B (This is true for GID/setgid, not SUID)"
  },
  {
    "question": "Which command is used to find the Inode number of a specific file?",
    "options": {
      "A": "ls -i",
      "B": "stat",
      "C": "inode-show",
      "D": "Both A and B"
    },
    "answer": "D"
  },
  {
    "question": "What is the function of the 'iptables' -P flag?",
    "options": {
      "A": "To set the default policy for a chain (e.g., DROP or ACCEPT).",
      "B": "To add a new port rule.",
      "C": "To print the current firewall table.",
      "D": "To purge all existing rules."
    },
    "answer": "A"
  },
  {
    "question": "True or False: The 'crontab' entry '0 0 * * *' will run a script every day at midnight.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO are common signals used to reload a daemon's configuration without stopping the process?",
    "options": {
      "A": "SIGHUP (1)",
      "B": "SIGUSR1",
      "C": "SIGKILL",
      "D": "SIGSTOP"
    },
    "answer": "A, B"
  },
  {
    "question": "What does the 'strace' utility primarily track?",
    "options": {
      "A": "CPU usage of a process.",
      "B": "System calls and signals made by a process.",
      "C": "Network bandwidth of an interface.",
      "D": "The number of users logged into a shell."
    },
    "answer": "B"
  },
  {
    "question": "True or False: Using 'unset' in a script removes a variable from the current shell environment.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to check the available entropy on a Linux system (critical for cryptography)?",
    "options": {
      "A": "cat /proc/sys/kernel/random/entropy_avail",
      "B": "entropy-check",
      "C": "rng-tools --show",
      "D": "ls-entropy"
    },
    "answer": "A"
  },
  {
    "question": "Identify TWO characteristics of a 'Named Pipe' (FIFO):",
    "options": {
      "A": "It appears as a file in the filesystem.",
      "B": "It allows communication between two unrelated processes.",
      "C": "It stores data permanently on the disk.",
      "D": "It is faster than a standard pipe (|)."
    },
    "answer": "A, B"
  },
  {
    "question": "What is the purpose of the 'sysctl' command?",
    "options": {
      "A": "To manage systemd services.",
      "B": "To configure kernel parameters at runtime.",
      "C": "To list all active system users.",
      "D": "To control the system clock."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'wait' command in Bash causes the shell to wait for all background jobs to finish before proceeding.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to create a backup of an entire disk partition bit-by-bit?",
    "options": {
      "A": "cp",
      "B": "dd",
      "C": "rsync",
      "D": "tar"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to find which shared libraries a specific binary is linked to at runtime?",
    "options": {
      "A": "ldd",
      "B": "ls-lib",
      "C": "objdump",
      "D": "readelf"
    },
    "answer": "A"
  },
  {
    "question": "True or False: The 'renice' command can be used to increase the priority (lower the nice value) of a process by a non-root user.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'OOM Killer' in the Linux kernel?",
    "options": {
      "A": "To kill processes that use too much CPU.",
      "B": "To terminate processes to free up memory when the system is critically low on RAM.",
      "C": "To prevent unauthorized users from logging in.",
      "D": "To delete temporary files during boot."
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO valid ways to create an alias that persists across reboots for a user:",
    "options": {
      "A": "Adding it to ~/.bashrc",
      "B": "Adding it to ~/.bash_profile",
      "C": "Running 'alias name=command' in the terminal.",
      "D": "Adding it to /tmp/aliases"
    },
    "answer": "A, B"
  },
  {
    "question": "Which specific file contains information about currently supported filesystems by the running kernel?",
    "options": {
      "A": "/proc/filesystems",
      "B": "/etc/filesystems",
      "C": "/sys/fs",
      "D": "/boot/config"
    },
    "answer": "A"
  },
  {
    "question": "True or False: A 'Hard Link' shares the same Inode number as the original file.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO signals are used for 'graceful termination' and 'forced termination' respectively?",
    "options": {
      "A": "SIGTERM (15)",
      "B": "SIGKILL (9)",
      "C": "SIGSTOP",
      "D": "SIGINT"
    },
    "answer": "A, B"
  },
  {
    "question": "What does the 'strace' command allow a developer to do?",
    "options": {
      "A": "Trace the path of a network packet.",
      "B": "Intercept and record system calls made by a process.",
      "C": "Trace the history of a file's edits.",
      "D": "Find the source code of a binary."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The /proc/sys directory allows you to modify kernel parameters at runtime without a reboot.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary function of 'Swap' space on a Linux system?",
    "options": {
      "A": "To swap files between different users.",
      "B": "To act as virtual memory on the disk when physical RAM is full.",
      "C": "To provide a backup for the root partition.",
      "D": "To speed up application launch times."
    },
    "answer": "B"
  },
  {
    "question": "Which TWO characters are used to redirect 'Standard Error' to a file in Bash?",
    "options": {
      "A": "2>",
      "B": "&>",
      "C": "1>",
      "D": ">>"
    },
    "answer": "A, B"
  },
  {
    "question": "True or False: The 'set -e' command in a script causes it to exit immediately if any command returns a non-zero exit status.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command is used to display the default runlevel or target in a systemd-based system?",
    "options": {
      "A": "runlevel",
      "B": "systemctl get-default",
      "C": "init status",
      "D": "who -r"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO directories that are part of the virtual 'Pseudo File System' in Linux:",
    "options": {
      "A": "/proc",
      "B": "/sys",
      "C": "/home",
      "D": "/usr"
    },
    "answer": "A, B"
  },
  {
    "question": "Which command is used to check the available entropy on a system (crucial for random number generation)?",
    "options": {
      "A": "cat /proc/sys/kernel/random/entropy_avail",
      "B": "entropy-check",
      "C": "ls-entropy",
      "D": "rng-status"
    },
    "answer": "A"
  },
  {
    "question": "True or False: The 'umask' value is subtracted from 666 for files and 777 for directories to determine default permissions.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the PID of the 'init' or 'systemd' process?",
    "options": {
      "A": "0",
      "B": "1",
      "C": "10",
      "D": "None of the above"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO components are required to set up a 'Chroot' jail?",
    "options": {
      "A": "A new root directory.",
      "B": "Necessary binary files and their library dependencies.",
      "C": "A network bridge.",
      "D": "A dedicated kernel."
    },
    "answer": "A, B"
  },
  {
    "question": "What is the purpose of 'sysctl'?",
    "options": {
      "A": "To list active system services.",
      "B": "To configure kernel parameters at runtime.",
      "C": "To control the system clock.",
      "D": "To manage system logs."
    },
    "answer": "B"
  },
  {
    "question": "True or False: Using 'kill -9' is the preferred way to terminate a database process safely.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to view the system boot messages (kernel ring buffer)?",
    "options": {
      "A": "cat /var/log/boot",
      "B": "dmesg",
      "C": "bootlog",
      "D": "klog"
    },
    "answer": "B"
  },
  {
    "question": "Identify TWO tools used to manage Logical Volumes in Linux:",
    "options": {
      "A": "pvcreate",
      "B": "vgextend",
      "C": "fdisk",
      "D": "mkfs"
    },
    "answer": "A, B"
  },
  {
    "question": "What does the 'sticky bit' do on a shared directory?",
    "options": {
      "A": "Prevents anyone but the file owner from deleting a file within that directory.",
      "B": "Makes all files within the directory read-only.",
      "C": "Speeds up the access to files in that directory.",
      "D": "Encrypts the directory contents."
    },
    "answer": "A"
  },
  {
    "question": "True or False: The 'export' command makes a variable available to all child processes of the current shell.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which command displays the hardware clock (RTC) rather than the system clock?",
    "options": {
      "A": "date",
      "B": "hwclock",
      "C": "timedatectl",
      "D": "time"
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
    skill = "Linux"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
