#!/usr/bin/env python3
"""
Quick setup wizard for Gmail SMTP with personal accounts
"""

import os
import re


def is_valid_email(email):
    """Simple email validation"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def is_app_password(password):
    """Check if password looks like a 16-character app password"""
    # App passwords are typically 16 characters, alphanumeric
    return len(password) == 16 and password.replace(" ", "").isalnum()


def setup_gmail_smtp():
    """Interactive setup for Gmail SMTP"""
    print("🥅 Total Keepers - Gmail SMTP Setup Wizard")
    print("=" * 50)

    print("\n📋 Prerequisites Check:")
    print("✅ Personal Gmail account")
    print("✅ 2-Factor Authentication enabled")
    print("✅ App password created")

    print("\n🔧 Configuration:")

    # Get Gmail address
    while True:
        email = input("\n📧 Enter your Gmail address: ").strip()
        if not email:
            print("❌ Email is required")
            continue
        if not email.endswith("@gmail.com"):
            print("❌ Please use a Gmail address (ending with @gmail.com)")
            continue
        if not is_valid_email(email):
            print("❌ Please enter a valid email address")
            continue
        break

    # Get app password
    while True:
        print("\n🔑 Enter your Gmail App Password:")
        print("   (16 characters from https://myaccount.google.com/apppasswords)")
        password = input("App Password: ").strip().replace(" ", "")

        if not password:
            print("❌ App password is required")
            continue
        if not is_app_password(password):
            print("❌ App password should be 16 characters")
            print("   Example: abcdefghijklmnop")
            continue
        break

    # Get display name
    display_name = input("\n👤 Sender name (default: Total Keepers): ").strip()
    if not display_name:
        display_name = "Total Keepers"

    # Update .env file
    env_path = ".env"
    if not os.path.exists(env_path):
        print(f"❌ {env_path} file not found")
        return False

    # Read current .env content
    with open(env_path, "r") as f:
        content = f.read()

    # Update SMTP settings
    replacements = {
        "SMTP_USERNAME=your-gmail@gmail.com": f"SMTP_USERNAME={email}",
        "SMTP_PASSWORD=your-16-char-app-password": f"SMTP_PASSWORD={password}",
        "SMTP_FROM_EMAIL=your-gmail@gmail.com": f"SMTP_FROM_EMAIL={email}",
        "SMTP_FROM_NAME=Total Keepers": f"SMTP_FROM_NAME={display_name}",
    }

    updated_content = content
    for old, new in replacements.items():
        updated_content = updated_content.replace(old, new)

    # Write updated content
    with open(env_path, "w") as f:
        f.write(updated_content)

    print("\n✅ Configuration saved to .env file!")

    # Show test command
    print("\n🧪 Test your setup:")
    print("   python scripts/test_gmail_smtp.py")

    print("\n💡 Tips:")
    print("   - Emails will appear to come from your Gmail address")
    print("   - Set Reply-To as no-reply@totalkeepers.com")
    print("   - Gmail has a daily sending limit of ~500 emails")

    return True


def main():
    """Main setup function"""
    try:
        if setup_gmail_smtp():
            print("\n🎉 Setup complete! You can now send emails via Gmail SMTP.")
        else:
            print("\n❌ Setup failed.")
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
