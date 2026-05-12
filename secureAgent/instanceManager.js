const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const crypto = require('crypto');

const APPDATA_DIR = path.join(process.env.APPDATA || '', 'VerifiHireSecureAgent');
const ID_FILE = path.join(APPDATA_DIR, 'instance.id');

/**
 * Generates or retrieves a persistent unique ID for this installation.
 * This ID is used to detect if the .exe is being reused for a second assessment.
 */
function getInstanceId() {
  try {
    if (!fs.existsSync(APPDATA_DIR)) {
      fs.mkdirSync(APPDATA_DIR, { recursive: true });
    }
    
    if (fs.existsSync(ID_FILE)) {
      return fs.readFileSync(ID_FILE, 'utf8').trim();
    }
    
    const newId = crypto.randomUUID();
    fs.writeFileSync(ID_FILE, newId, 'utf8');
    return newId;
  } catch (err) {
    console.error('[instance] Failed to manage instance ID:', err.message);
    return 'temp-' + Date.now();
  }
}

/**
 * Triggers the "Self-Destruct" sequence.
 * Creates a batch file that waits for a delay, deletes the .exe, and deletes itself.
 * @param {number} delaySeconds - Delay before deletion (e.g. 1800 for 30 minutes).
 */
function selfDestruct(delaySeconds = 0) {
  if (process.platform !== 'win32') {
    console.log('[instance] Self-destruct only supported on Windows');
    process.exit(0);
    return;
  }

  // Use process.execPath to get the path to the current running .exe
  const exePath = process.execPath;
  const batPath = path.join(path.dirname(exePath), 'cleanup_verifihire.bat');

  /**
   * The batch script logic:
   * 1. Wait for delaySeconds (using timeout)
   * 2. Attempt to delete the .exe (retrying if still locked)
   * 3. Delete the local ID folder to ensure no traces are left
   * 4. Delete itself
   */
  const batContent = `@echo off
setlocal enabledelayedexpansion

if ${delaySeconds} GTR 0 (
  echo Waiting for cleanup period...
  timeout /t ${delaySeconds} /nobreak > nul
) else (
  timeout /t 2 /nobreak > nul
)

:retry
echo Attempting to remove Secure Agent...
del /f /q "${exePath}"
if exist "${exePath}" (
  echo File still locked, retrying in 5 seconds...
  timeout /t 5 /nobreak > nul
  goto retry
)

echo Cleaning up local data...
rmdir /s /q "${APPDATA_DIR}"

echo Cleanup complete.
del /f /q "%~f0"
`;

  try {
    fs.writeFileSync(batPath, batContent, 'utf8');
    
    // Launch the batch script minimized so it doesn't disturb the user
    spawn('cmd.exe', ['/c', 'start', '/min', 'cmd.exe', '/c', batPath], {
      detached: true,
      stdio: 'ignore'
    });

    console.log(`[instance] Agent scheduled for auto-deletion in ${delaySeconds}s. Goodbye!`);
    
    // Exit the current process quickly
    setTimeout(() => {
      process.exit(0);
    }, 1000);
  } catch (err) {
    console.error('[instance] Failed to initiate cleanup:', err.message);
    process.exit(0);
  }
}

module.exports = { getInstanceId, selfDestruct };
