"""
Douyin Cookie Helper

This script helps you get cookies from Douyin for use with yt-dlp.

Usage:
    1. Open Chrome/Edge and visit https://www.douyin.com
    2. Make sure you're logged in (optional but recommended)
    3. Run this script: python get_douyin_cookies.py
    4. Follow the instructions to paste your cookies
"""

import os
import sys

COOKIE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")

def check_cookies():
    """Check if cookies.txt exists and is valid."""
    if not os.path.exists(COOKIE_FILE):
        print(f"Cookie file not found: {COOKIE_FILE}")
        print("\nTo get cookies:")
        print("1. Install 'Get cookies.txt LOCALLY' browser extension")
        print("2. Visit https://www.douyin.com while logged in")
        print("3. Click the extension icon and export cookies")
        print("4. Save as cookies.txt in this directory")
        return False

    with open(COOKIE_FILE, 'r') as f:
        content = f.read()

    if 'ttwid' in content or '__ac_nonce' in content:
        print("Cookie file looks valid!")
        print(f"Location: {COOKIE_FILE}")
        return True
    else:
        print("Cookie file exists but may be missing required cookies.")
        print("Required cookies: ttwid, __ac_nonce, msToken")
        return False

def create_sample_cookies():
    """Create a sample cookies.txt file."""
    sample = """# Netscape HTTP Cookie File
# This is a sample file. Replace with your actual cookies from Douyin.

.douyin.com	TRUE	/	FALSE	0	ttwid	YOUR_TTWID_HERE
.douyin.com	TRUE	/	FALSE	0	__ac_nonce	YOUR_NONCE_HERE
.douyin.com	TRUE	/	FALSE	0	msToken	YOUR_TOKEN_HERE
"""
    with open(COOKIE_FILE, 'w') as f:
        f.write(sample)
    print(f"Sample cookie file created at: {COOKIE_FILE}")
    print("Please replace the placeholder values with your actual cookies.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create-sample":
        create_sample_cookies()
    else:
        if check_cookies():
            print("\nYou can now use the douyin-render-markdown skill!")
            print("Example: /douyin-render-markdown https://v.douyin.com/xxxxx/")
        else:
            print("\nRun with --create-sample to create a sample cookie file.")
