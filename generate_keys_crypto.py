from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import base64

private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# Get private key as integer (scalar)
private_val = private_key.private_numbers().private_value
private_bytes = private_val.to_bytes(32, byteorder='big')
private_b64 = base64.urlsafe_b64encode(private_bytes).strip(b'=').decode('utf-8')

# Get public key as raw bytes (uncompressed point)
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)
public_b64 = base64.urlsafe_b64encode(public_bytes).strip(b'=').decode('utf-8')

print(f"VAPID_PRIVATE_KEY={private_b64}")
print(f"NEXT_PUBLIC_VAPID_PUBLIC_KEY={public_b64}")
