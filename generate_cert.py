#!/usr/bin/env python3

from OpenSSL import crypto
import os

# Generate key pair
key = crypto.PKey()
key.generate_key(crypto.TYPE_RSA, 2048)

# Generate certificate
cert = crypto.X509()
cert.get_subject().C = "US"
cert.get_subject().ST = "State"
cert.get_subject().L = "City"
cert.get_subject().O = "Organization"
cert.get_subject().OU = "Organizational Unit"
cert.get_subject().CN = "localhost"
cert.set_serial_number(1)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(365*24*60*60)  # 1 year
cert.set_issuer(cert.get_subject())
cert.set_pubkey(key)
cert.sign(key, 'sha256')

# Write certificate and key to files
with open("cert.pem", "wt") as f:
    f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode())

with open("key.pem", "wt") as f:
    f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode())

print("Certificate and key generated successfully!")
print("Files created: cert.pem, key.pem")
