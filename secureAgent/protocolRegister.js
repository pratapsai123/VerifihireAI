/**
 * Register / unregister the verifihire:// custom URL protocol on Windows.
 * Only the packaged .exe should register — never Node dev mode.
 */
const { execSync } = require('child_process');
const path = require('path');

const REG_BASE = 'HKCU\\Software\\Classes\\verifihire';

function isPackagedAgent() {
  return Boolean(process.pkg);
}

function registerProtocol() {
  if (process.platform !== 'win32') {
    console.log('[protocol] Skipping protocol registration (non-Windows platform)');
    return;
  }

  if (!isPackagedAgent()) {
    console.log('[protocol] Skipping registration (not a packaged .exe)');
    return;
  }

  try {
    const launchCommand = `\\"${process.execPath}\\"`;

    execSync(`reg add "${REG_BASE}" /ve /d "URL:VerifiHire Secure Agent Protocol" /f`, { stdio: 'ignore' });
    execSync(`reg add "${REG_BASE}" /v "URL Protocol" /d "" /f`, { stdio: 'ignore' });
    execSync(`reg add "${REG_BASE}\\shell\\open\\command" /ve /d "${launchCommand}" /f`, { stdio: 'ignore' });

    console.log('[protocol] verifihire:// protocol registered');
    console.log('[protocol] Launch command:', launchCommand.replace(/\\"/g, '"'));
  } catch (err) {
    console.error('[protocol] Registration failed:', err.message);
  }
}

function unregisterProtocol() {
  if (process.platform !== 'win32') {
    return;
  }

  try {
    execSync(`reg delete "${REG_BASE}" /f`, { stdio: 'ignore' });
    console.log('[protocol] verifihire:// protocol unregistered');
  } catch (err) {
    // Key may already be absent
    if (!String(err.message || '').includes('unable to find')) {
      console.warn('[protocol] Unregister failed:', err.message);
    }
  }
}

module.exports = { registerProtocol, unregisterProtocol };
