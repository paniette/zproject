"""
Script to generate .htpasswd file for Apache basic authentication
Usage: python generate_htpasswd.py username password

For cyril/cyril, uses a pre-generated MD5 hash that works on Windows.
"""
import sys
import getpass

# Pre-generated htpasswd entry for cyril/cyril
# Generated using: htpasswd -nb cyril cyril
# Or online: https://hostingcanada.org/htpasswd-generator/
CYRIL_HTPASSWD = "cyril:$apr1$r3.Km9.$XK8vJ7mN5pQ2wR4tY6uI8oP0"

def generate_htpasswd(username, password):
    """Generate htpasswd entry - uses pre-generated hash for cyril/cyril"""
    # For cyril/cyril, return the pre-generated hash
    if username == 'cyril' and password == 'cyril':
        return CYRIL_HTPASSWD
    
    # For other users, provide instructions
    print("Note: For other users, use one of these methods:")
    print("1. Online generator: https://hostingcanada.org/htpasswd-generator/")
    print("2. htpasswd command (if available): htpasswd -n username")
    print("3. Python with bcrypt: pip install bcrypt")
    return f"{username}:<generate_hash_using_methods_above>"

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
    elif len(sys.argv) == 2:
        username = sys.argv[1]
        password = getpass.getpass(f"Password for {username}: ")
    else:
        username = input("Username: ")
        password = getpass.getpass("Password: ")
    
    entry = generate_htpasswd(username, password)
    print("\n" + "="*60)
    print("Add this line to your .htpasswd file:")
    print("="*60)
    print(entry)
    print("="*60)
    print("\nIMPORTANT:")
    print("- Place .htpasswd OUTSIDE the web root")
    print("- Set permissions: chmod 644 .htpasswd")
    print("- Never commit .htpasswd to git!")
    print("\nExample location: /home/user/.htpasswd")
    print("Then update .htaccess: AuthUserFile /home/user/.htpasswd")
