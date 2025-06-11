# Generate self-signed certificates for HTTPS development using PowerShell
# This script creates localhost SSL certificates for development

try {
    # Create a self-signed certificate for localhost
    $cert = New-SelfSignedCertificate -DnsName "localhost" -CertStoreLocation "cert:\LocalMachine\My" -KeyUsage DigitalSignature -KeyExportPolicy Exportable -KeySpec Signature -KeyLength 2048 -KeyAlgorithm RSA -Subject "CN=localhost"
    
    # Export the certificate to PEM format
    $certPath = ".\certs\localhost.pem"
    $keyPath = ".\certs\localhost-key.pem"
    
    # Export certificate
    $certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
    $certPem = "-----BEGIN CERTIFICATE-----`n" + [System.Convert]::ToBase64String($certBytes, [System.Base64FormattingOptions]::InsertLineBreaks) + "`n-----END CERTIFICATE-----"
    $certPem | Out-File -FilePath $certPath -Encoding ASCII
    
    Write-Host "SSL certificate generated successfully at: $certPath"
    Write-Host ""
    Write-Host "Note: For the private key, you may need to use a tool like OpenSSL or mkcert."
    Write-Host "Alternative: Use the Vite dev server without HTTPS for development."
    Write-Host ""
    Write-Host "To disable HTTPS in development, remove the 'https' section from vite.config.ts"
    
    # Clean up - remove from certificate store
    Remove-Item -Path "cert:\LocalMachine\My\$($cert.Thumbprint)" -Force
}
catch {
    Write-Host "Error generating certificate: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Alternative: Disable HTTPS in vite.config.ts for development"
}
