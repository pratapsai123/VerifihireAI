const path = require('path');
const fs = require('fs');

async function setIcon() {
  try {
    const pngPath = path.join(__dirname, '..', 'frontend', 'public', 'assets', 'VerifiHireAI_logo.png');
    const icoPath = path.join(__dirname, 'logo.ico');
    const exePath = path.join(__dirname, 'VerifiHireSecureAgent.exe');

    if (!fs.existsSync(pngPath)) {
      console.warn('Warning: Logo not found at', pngPath);
      console.warn('Skipping icon injection.');
      return;
    }

    console.log('Converting VerifiHire logo to Windows .ico format...');
    const { default: pngToIco } = await import('png-to-ico');
    const buf = await pngToIco(pngPath);
    fs.writeFileSync(icoPath, buf);

    console.log('Injecting icon into VerifiHireSecureAgent.exe...');
    console.warn(
      'Warning: rcedit can corrupt pkg-built executables. Prefer "npm run build" without icon.'
    );
    const { rcedit } = await import('rcedit');
    await rcedit(exePath, {
      icon: icoPath,
      'version-string': {
        CompanyName: 'VerifiHire',
        FileDescription: 'VerifiHire Secure Agent',
        ProductName: 'VerifiHire Secure Agent',
        OriginalFilename: 'VerifiHireSecureAgent.exe'
      }
    });


    console.log('Icon successfully added!');
  } catch (err) {
    console.error('Failed to add icon:', err);
    process.exit(1);
  }
}

setIcon();
