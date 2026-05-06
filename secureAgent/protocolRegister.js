/**
 * Register the verifihire:// custom URL protocol on Windows.
 * This allows the browser to auto-launch VerifiHireSecureAgent.exe
 * when a candidate opens an assessment/interview link.
 *
 * Similar to how Zoom registers zoommtg:// or Teams registers msteams://
 */
const { execSync } = require('child_process');
const path = require('path');

function registerProtocol() {
  if (process.platform !== 'win32') {
    console.log('[protocol] Skipping protocol registration (non-Windows platform)');
    return;
  }

  try {
    // Determine the executable path
    // When compiled with pkg: process.execPath = path to the .exe
    // When running with node: process.execPath = path to node.exe
    const isPackaged = !process.execPath.toLowerCase().endsWith('node.exe') &&
                       !process.execPath.toLowerCase().endsWith('node');

    let launchCommand;
    if (isPackaged) {
      // Compiled .exe — just launch the exe directly
      launchCommand = `\\"${process.execPath}\\"`;
    } else {
      // Running via node — need to call node with the server script
      const serverPath = path.resolve(__dirname, 'server.js');
      launchCommand = `\\"${process.execPath}\\" \\"${serverPath}\\"`;
    }

    const regBase = 'HKCU\\Software\\Classes\\verifihire';

    // Set the protocol description
    execSync(`reg add "${regBase}" /ve /d "URL:VerifiHire Secure Agent Protocol" /f`, { stdio: 'ignore' });

    // Mark this key as a URL protocol handler
    execSync(`reg add "${regBase}" /v "URL Protocol" /d "" /f`, { stdio: 'ignore' });

    // Set the command to execute when verifihire:// is triggered
    execSync(`reg add "${regBase}\\shell\\open\\command" /ve /d "${launchCommand}" /f`, { stdio: 'ignore' });

    console.log('[protocol] verifihire:// protocol registered successfully');
    console.log('[protocol] Launch command:', launchCommand.replace(/\\"/g, '"'));
  } catch (err) {
    console.error('[protocol] Registration failed:', err.message);
  }
}

module.exports = { registerProtocol };
