const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const crypto = require('crypto');
const { unregisterProtocol } = require('./protocolRegister');

const APPDATA_DIR = path.join(process.env.APPDATA || '', 'VerifiHireSecureAgent');
const LEGACY_ID_FILE = path.join(APPDATA_DIR, 'instance.id');

/**
 * Packaged .exe: store instance id beside the binary so each download gets its own id.
 * Dev (node server.js): fall back to APPDATA.
 */
function getInstanceIdPath() {
  if (process.pkg) {
    return path.join(path.dirname(process.execPath), '.verifihire-instance');
  }
  if (!fs.existsSync(APPDATA_DIR)) {
    fs.mkdirSync(APPDATA_DIR, { recursive: true });
  }
  return LEGACY_ID_FILE;
}

function writeInstanceId(idPath, newId) {
  fs.writeFileSync(idPath, newId, 'utf8');
}

/**
 * Generates or retrieves a unique ID for this agent installation.
 * Each downloaded .exe gets its own id file — never reuse legacy APPDATA ids.
 */
function getInstanceId() {
  const newId = crypto.randomUUID();

  try {
    const idPath = getInstanceIdPath();

    if (fs.existsSync(idPath)) {
      const existing = fs.readFileSync(idPath, 'utf8').trim();
      if (existing && !existing.startsWith('temp-')) {
        return existing;
      }
    }

    try {
      writeInstanceId(idPath, newId);
      return newId;
    } catch (writeErr) {
      // Downloads folder may be read-only — fall back to APPDATA (fresh file per install attempt)
      if (!fs.existsSync(APPDATA_DIR)) {
        fs.mkdirSync(APPDATA_DIR, { recursive: true });
      }
      const fallbackPath = path.join(APPDATA_DIR, 'instance.id');
      if (fs.existsSync(fallbackPath)) {
        const existing = fs.readFileSync(fallbackPath, 'utf8').trim();
        if (existing && !existing.startsWith('temp-')) {
          return existing;
        }
      }
      writeInstanceId(fallbackPath, newId);
      return newId;
    }
  } catch (err) {
    console.error('[instance] Failed to manage instance ID:', err.message);
    return 'temp-' + Date.now();
  }
}

/**
 * Triggers the "Self-Destruct" sequence.
 * Creates a batch file that waits for a delay, deletes the .exe, instance file, and itself.
 * @param {number} delaySeconds - Delay before deletion (0 = immediate after process exit).
 */
function selfDestruct(delaySeconds = 0) {
  if (process.platform !== 'win32') {
    console.log('[instance] Self-destruct only supported on Windows');
    process.exit(0);
    return;
  }

  unregisterProtocol();

  const exePath = process.execPath;
  const exeDir = path.dirname(exePath);
  const batPath = path.join(exeDir, 'cleanup_verifihire.bat');
  const instancePath = getInstanceIdPath();

  const batContent = `@echo off
setlocal enabledelayedexpansion

if ${delaySeconds} GTR 0 (
  echo Waiting for cleanup period...
  timeout /t ${delaySeconds} /nobreak > nul
) else (
  timeout /t 2 /nobreak > nul
)

echo Stopping any other VerifiHire Secure Agent copies...
taskkill /F /IM VerifiHireSecureAgent.exe /T >nul 2>&1
timeout /t 2 /nobreak > nul

:retry
echo Attempting to remove Secure Agent...
del /f /q "${exePath}"
if exist "${exePath}" (
  echo File still locked, retrying in 5 seconds...
  timeout /t 5 /nobreak > nul
  goto retry
)

if exist "${instancePath}" del /f /q "${instancePath}"
if exist "${LEGACY_ID_FILE}" del /f /q "${LEGACY_ID_FILE}"
echo Cleaning up local data...
if exist "${APPDATA_DIR}" rmdir /s /q "${APPDATA_DIR}"

echo Cleanup complete.
del /f /q "%~f0"
`;

  try {
    fs.writeFileSync(batPath, batContent, 'utf8');

    spawn('cmd.exe', ['/c', 'start', '/min', 'cmd.exe', '/c', batPath], {
      detached: true,
      stdio: 'ignore',
    });

    console.log(`[instance] Agent scheduled for auto-deletion in ${delaySeconds}s. Goodbye!`);

    setTimeout(() => {
      process.exit(0);
    }, 1000);
  } catch (err) {
    console.error('[instance] Failed to initiate cleanup:', err.message);
    process.exit(0);
  }
}

module.exports = { getInstanceId, selfDestruct };
