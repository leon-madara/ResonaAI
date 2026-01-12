"""
Generate UI Config for Existing User
Quick script to create voice sessions and generate UI for a user by email
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.database.models import User, VoiceSession
import uuid
from datetime import datetime, timedelta

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:9009@localhost:5432/mental_health"
)

async def generate_ui_for_user(email: str):
    """Generate voice sessions and UI config for a user"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Find user by email
        result = session.execute(
            text("SELECT user_id FROM users WHERE email = :email"),
            {"email": email}
        )
        row = result.fetchone()
        
        if not row:
            print(f"[ERROR] User with email {email} not found")
            return None
        
        user_id = str(row[0])
        print(f"[OK] Found user: {user_id}")
        
        # Import the fake data generator
        from scripts.create_fake_user_data import FakeUserDataGenerator
        
        generator = FakeUserDataGenerator(DATABASE_URL)
        
        # Create voice sessions
        print("\n[INFO] Creating voice sessions...")
        session_ids = generator.create_fake_voice_sessions(user_id, num_sessions=10)
        
        # Run pattern analysis
        print("\n[INFO] Running pattern analysis...")
        patterns = await generator.analyze_patterns(user_id)
        
        if patterns:
            print("[OK] Patterns analyzed successfully")
        
        # Build UI
        print("\n[INFO] Building UI configuration...")
        ui_config = await generator.build_ui(user_id)
        
        if ui_config:
            print("[OK] UI configuration generated successfully")
            print(f"  - Changes detected: {ui_config.get('changes_count', 0)}")
        
        print("\n[SUCCESS] UI generation complete!")
        print(f"\nUser ID: {user_id}")
        print("You can now test the UI config at: http://localhost:3000/ui-test")
        
        return user_id
        
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        session.close()

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "testuser@example.com"
    print(f"Generating UI config for user: {email}")
    asyncio.run(generate_ui_for_user(email))
