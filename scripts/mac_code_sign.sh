# 1. Create a self-signed certificate
security create-keychain -p github_action_keychain build.keychain
security default-keychain -s build.keychain
security unlock-keychain -p github_action_keychain build.keychain

# 2. Create a self-signed certificate
openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 \
  -nodes -keyout private.key -out developer.crt \
  -subj "/CN=Developer ID Application: Dipjyoti Metia" \
  -addext "subjectAltName=DNS:com.friday.app"

# 3. Create a p12 file
openssl pkcs12 -export -out developer.p12 \
  -inkey private.key -in developer.crt \
  -password pass:your_password

# 4. Convert the p12 to base64 for GitHub Secrets
base64 -i developer.p12 | pbcopy  # This copies to clipboard on macOS

# # Add this to your GitHub workflow
# security:
#   if: matrix.os == 'macos-latest'
#   run: |
#     echo $MACOS_CERTIFICATE | base64 --decode > certificate.p12
#     security create-keychain -p builder_keychain build.keychain
#     security default-keychain -s build.keychain
#     security unlock-keychain -p builder_keychain build.keychain
#     security import certificate.p12 -k build.keychain -P $MACOS_CERTIFICATE_PWD -T /usr/bin/codesign
#     security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k builder_keychain build.keychain
#   env:
#     MACOS_CERTIFICATE: ${{ secrets.MACOS_CERTIFICATE }}
#     MACOS_CERTIFICATE_PWD: ${{ secrets.MACOS_CERTIFICATE_PWD }}