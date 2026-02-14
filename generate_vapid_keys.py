from pywebpush import Vapid

vapid = Vapid()
vapid.generate_keys()

print(f"VAPID_PRIVATE_KEY={vapid.private_key}")
print(f"VAPID_PUBLIC_KEY={vapid.public_key}")
print(f"VAPID_MAILTO=mailto:admin@flowfunds.com")
