# 1. Create a self-signed certificate using PowerShell
$cert = New-SelfSignedCertificate -Type Custom -Subject "CN=Your Name" -KeyUsage DigitalSignature -FriendlyName "Your App Cert" -CertStoreLocation "Cert:\CurrentUser\My" -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

# 2. Export the certificate with private key
$password = ConvertTo-SecureString -String "your_password" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath developer.pfx -Password $password

# 3. Convert the pfx to base64 for GitHub Secrets
$pfxBytes = Get-Content developer.pfx -Encoding Byte
[System.Convert]::ToBase64String($pfxBytes) | Set-Clipboard  # Copies to clipboard

# # Add this to your GitHub workflow
# signing:
#   if: matrix.os == 'windows-latest'
#   run: |
#     echo ${{ secrets.WINDOWS_CERTIFICATE }} | base64 --decode > certificate.pfx
#     SignTool sign /f certificate.pfx /p ${{ secrets.WINDOWS_CERTIFICATE_PWD }} /tr http://timestamp.sectigo.com /td sha256 /fd sha256 your-app.exe
#   env:
#     WINDOWS_CERTIFICATE: ${{ secrets.WINDOWS_CERTIFICATE }}
#     WINDOWS_CERTIFICATE_PWD: ${{ secrets.WINDOWS_CERTIFICATE_PWD }}