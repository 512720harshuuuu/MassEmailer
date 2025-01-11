import smtplib
import os
from dotenv import load_dotenv

def test_gmail_connection():
    # Force reload environment variables
    load_dotenv(override=True)
    
    # Print all environment variables for debugging
    print("All environment variables:")
    for key, value in os.environ.items():
        if 'PASSWORD' in key or 'EMAIL' in key:
            print(f"{key}: {value}")
    
    EMAIL = os.getenv('SENDER_EMAIL')
    PASSWORD = os.getenv('SENDER_PASSWORD')
    
    print("\nDirect .env reading:")
    with open('.env', 'r') as f:
        print(f.read())
        
    print("\nValues being used:")
    print(f"Email: {EMAIL}")
    print(f"Password length: {len(PASSWORD) if PASSWORD else 'None'}")
    print(f"Password: {PASSWORD}")
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        print("1. Server connection successful")
        
        server.starttls()
        print("2. TLS started")
        
        server.login(EMAIL.strip(), PASSWORD.strip())
        print("3. Login successful")
        
        server.quit()
        print("4. Test completed successfully")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    test_gmail_connection()