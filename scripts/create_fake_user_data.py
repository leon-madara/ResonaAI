"""
Create Fake User Data for Testing UI Generation

This script creates a test user with fake voice session data that simulates:
- A stressed user
- Who enjoys fashion
- And watches drama movies on Netflix

Then triggers pattern analysis and UI generation to test the adaptive interface.
"""

import asyncio
import uuid
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List
import json
from pathlib import Path

# Add project root to Python path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Database imports
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.database.models import User, VoiceSession, Base

# Pattern analysis and UI builder will be imported conditionally in functions
# Some modules may not be fully implemented yet

# Database connection from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:9009@localhost:5432/mental_health"
)

class FakeUserDataGenerator:
    """Generate fake user data for testing"""
    
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_test_user(self) -> str:
        """Create a test user and return user_id"""
        session = self.Session()
        try:
            user = User(
                user_id=uuid.uuid4(),
                anonymous_id=f"test_user_{uuid.uuid4().hex[:8]}",
                account_status='active',
                timezone='Africa/Nairobi'
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"[OK] Created test user: {user.anonymous_id} ({user.user_id})")
            return str(user.user_id)
        finally:
            session.close()
    
    def create_fake_voice_sessions(self, user_id: str, num_sessions: int = 10) -> List[str]:
        """
        Create fake voice sessions with transcripts that include:
        - Stress/anxiety indicators
        - Fashion interests
        - Netflix drama movie mentions
        """
        session = self.Session()
        session_ids = []
        
        # Sample transcripts that reflect the user profile
        transcripts = [
            # Stressed + Fashion
            "I've been so stressed lately. Work is overwhelming. But I did go shopping yesterday and found this amazing dress. Fashion always helps me feel better, you know?",
            
            # Stressed + Netflix
            "I'm feeling really anxious today. I couldn't sleep last night. I ended up watching this drama on Netflix, it was so intense. Sometimes watching shows helps me escape.",
            
            # Fashion interest
            "I love following fashion trends. It's one of the few things that brings me joy. I spent hours looking at fashion blogs today.",
            
            # Netflix drama
            "I watched this amazing drama series on Netflix last night. It was so emotional, I cried through half of it. But it felt good to feel something, you know?",
            
            # Stressed + both interests
            "I'm really stressed about money and everything. But I'm planning to watch a new drama on Netflix tonight. And I'm thinking about updating my wardrobe, maybe that will help me feel better.",
            
            # More stress
            "I feel like I'm drowning. Everything is too much. I don't know how to cope anymore.",
            
            # Fashion as coping
            "When I'm stressed, I like to look at fashion magazines. It's my escape. I imagine wearing beautiful clothes and feeling confident.",
            
            # Netflix as coping
            "I've been watching so many drama movies on Netflix lately. They help me forget about my problems for a while. I watched three episodes last night.",
            
            # Mixed stress
            "I'm anxious about everything. My job, my relationships, my future. I don't know what to do.",
            
            # Fashion + Netflix together
            "I love drama shows on Netflix, especially the ones with beautiful costumes. Fashion and storytelling together, that's my thing. It helps when I'm feeling down."
        ]
        
        # Voice emotions (mostly stressed/sad, some neutral) - must match schema constraint
        # Valid: 'neutral', 'happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'hopeless', 'resigned', 'numb'
        emotions = ['fear', 'sad', 'fear', 'neutral', 'fear', 'sad', 'neutral', 'fear', 'sad', 'neutral']
        
        # Voice features that indicate stress
        stressed_voice_features = {
            'prosodic': {
                'pitch_mean': 180,  # Slightly higher when stressed
                'pitch_std': 45,    # More variability
                'pitch_range': 180,
                'energy_mean': 0.4,  # Lower energy
                'energy_std': 0.12
            },
            'spectral': {
                'zero_crossing_rate': 0.14,  # Slightly harsh
                'spectral_centroid': 2500
            },
            'temporal': {
                'speech_rate': 4.2,  # Faster when anxious
                'pause_ratio': 0.25   # More pauses
            }
        }
        
        try:
            for i in range(num_sessions):
                # Create session timestamp (spread over last 2 weeks)
                days_ago = (num_sessions - i) * 1.4  # Spread sessions
                session_start = datetime.now() - timedelta(days=days_ago)
                session_end = session_start + timedelta(seconds=120)  # 2 min session
                
                # Get transcript and emotion for this session
                transcript = transcripts[i % len(transcripts)]
                emotion = emotions[i % len(emotions)]
                
                # Create voice session
                voice_session = VoiceSession(
                    session_id=uuid.uuid4(),
                    user_id=uuid.UUID(user_id),
                    session_start=session_start,
                    session_end=session_end,
                    duration_seconds=120,
                    voice_emotion=emotion,
                    emotion_confidence=0.75 + (i % 3) * 0.08,  # 0.75-0.91
                    voice_features=stressed_voice_features,
                    transcript_encrypted=transcript,  # In real app, this would be encrypted
                    transcript_language='en',
                    processed=True,
                    patterns_extracted=False  # Will be extracted by pattern analysis
                )
                
                session.add(voice_session)
                session_ids.append(str(voice_session.session_id))
            
            session.commit()
            print(f"[OK] Created {num_sessions} fake voice sessions")
            return session_ids
            
        finally:
            session.close()
    
    async def analyze_patterns(self, user_id: str):
        """Run pattern analysis on the fake sessions"""
        print("\n[INFO] Analyzing patterns from voice sessions...")
        
        # Try to import pattern analysis modules
        try:
            from src.database.pattern_storage import PatternStorageService
            from src.pattern_analysis.pattern_aggregator import PatternAggregator
        except ImportError as e:
            print(f"[WARNING] Pattern analysis modules not available: {e}")
            print("[INFO] Skipping pattern analysis - user and sessions created successfully")
            return None
        
        # Get sessions from database
        session = self.Session()
        try:
            pattern_storage = PatternStorageService(session)
            
            # Get sessions for pattern analysis
            sessions = await pattern_storage.get_session_history(user_id, days=30)
            
            if not sessions:
                print("[WARNING] No sessions found for pattern analysis")
                return None
            
            print(f"[OK] Found {len(sessions)} sessions to analyze")
            
            # Run pattern aggregator
            aggregator = PatternAggregator()
            patterns = await aggregator.aggregate(user_id, sessions)
            
            # Store patterns
            await pattern_storage.store_patterns(user_id, patterns)
            
            print(f"[OK] Patterns analyzed and stored")
            print(f"  - Primary emotions: {patterns.emotional_patterns.primary_emotions}")
            print(f"  - Risk level: {patterns.current_risk.risk_level}")
            print(f"  - Effective coping: {[s.name for s in patterns.coping_profile.effective_strategies]}")
            
            return patterns
            
        except Exception as e:
            print(f"[WARNING] Pattern analysis failed: {e}")
            return None
        finally:
            session.close()
    
    async def build_ui(self, user_id: str):
        """Build UI configuration from patterns"""
        print("\n[INFO] Building UI configuration...")
        
        # Try to import UI builder modules
        try:
            from src.database.pattern_storage import PatternStorageService
            from src.overnight_builder.orchestrator import OvernightBuilder
            from src.overnight_builder.ui_config_generator import UIConfigGenerator
        except ImportError as e:
            print(f"[WARNING] UI Builder modules not available: {e}")
            print("[INFO] Skipping UI generation - user and sessions created successfully")
            return None
        
        session = self.Session()
        try:
            pattern_storage = PatternStorageService(session)
            
            # Get current patterns
            patterns_dict = await pattern_storage.get_current_patterns(user_id)
            
            if not patterns_dict:
                print("[WARNING] No patterns found for UI generation")
                return None
            
            # Build UI
            builder = OvernightBuilder(
                pattern_storage=pattern_storage,
                ui_generator=UIConfigGenerator()
            )
            
            user_dict = {'user_id': user_id}
            result = await builder.build_interface_for_user(user_dict, dry_run=False)
            
            if result.get('status') == 'success':
                print(f"[OK] UI configuration built successfully")
                print(f"  - Changes detected: {result.get('changes_count', 0)}")
                return result
            else:
                print(f"[WARNING] UI build skipped: {result.get('reason')}")
                return None
                
        except Exception as e:
            print(f"[WARNING] UI build failed: {e}")
            return None
        finally:
            session.close()
    
    async def get_ui_config(self, user_id: str) -> Dict:
        """Retrieve the generated UI configuration"""
        try:
            from src.database.pattern_storage import PatternStorageService
        except ImportError:
            print("\n[WARNING] Pattern storage not available - skipping UI config retrieval")
            return None
            
        session = self.Session()
        try:
            pattern_storage = PatternStorageService(session)
            
            config = await pattern_storage.get_latest_interface_config(user_id)
            
            if config:
                print("\n[INFO] Generated UI Configuration:")
                print(f"  - Theme: {config.get('theme', {}).get('name', 'N/A')}")
                print(f"  - Visible components: {len(config.get('components', {}))}")
                print(f"  - Layout priority: {config.get('layout', {}).get('priority', [])[:3]}...")
                
                # Show component details
                components = config.get('components', {})
                for comp_name, comp_config in list(components.items())[:5]:
                    visible = comp_config.get('visible', False)
                    prominence = comp_config.get('prominence', 'normal')
                    print(f"    - {comp_name}: visible={visible}, prominence={prominence}")
            else:
                print("\n[WARNING] No UI configuration found")
            
            return config
            
        except Exception as e:
            print(f"[WARNING] Failed to retrieve UI config: {e}")
            return None
        finally:
            session.close()


async def main():
    """Main execution"""
    print("=" * 60)
    print("Creating Fake User Data for UI Testing")
    print("=" * 60)
    
    # Initialize generator
    generator = FakeUserDataGenerator(DATABASE_URL)
    
    # Step 1: Create test user
    print("\n[STEP 1] Creating test user...")
    user_id = generator.create_test_user()
    
    # Step 2: Create fake voice sessions
    print("\n[STEP 2] Creating fake voice sessions...")
    session_ids = generator.create_fake_voice_sessions(user_id, num_sessions=10)
    
    # Step 3: Analyze patterns
    print("\n[STEP 3] Running pattern analysis...")
    patterns = await generator.analyze_patterns(user_id)
    
    if not patterns:
        print("[INFO] Pattern analysis skipped or failed. User and sessions created successfully.")
        print("[INFO] You can manually run pattern analysis later or check database connection.")
    
    # Step 4: Build UI
    print("\n[STEP 4] Building UI configuration...")
    ui_result = await generator.build_ui(user_id)
    
    # Step 5: Retrieve and display UI config
    print("\n[STEP 5] Retrieving UI configuration...")
    ui_config = await generator.get_ui_config(user_id)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Test data creation complete!")
    print("=" * 60)
    print(f"\nTest user ID: {user_id}")
    print(f"Number of sessions created: {len(session_ids)}")
    print(f"\nYou can now:")
    print(f"  - Query the database to see the test user and sessions")
    print(f"  - Run pattern analysis manually if modules are available")
    print(f"  - Test UI generation when the overnight builder is ready")
    print(f"\nExpected patterns in the data:")
    print(f"  - User shows stress/anxiety in voice emotions")
    print(f"  - Transcripts mention fashion interests")
    print(f"  - Transcripts mention Netflix drama shows")
    print(f"  - Coping strategies should include 'entertainment' (Netflix)")


if __name__ == "__main__":
    import sys
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL") and DATABASE_URL == "postgresql://postgres:password@localhost:5432/resona_db":
        print("⚠ WARNING: Using default DATABASE_URL")
        print("⚠ Set DATABASE_URL environment variable or update the default in the script")
        print()
    
    # Ask for confirmation
    print("=" * 60)
    print("This script will:")
    print("  1. Create a test user in your database")
    print("  2. Create 10 fake voice sessions")
    print("  3. Run pattern analysis")
    print("  4. Generate UI configuration")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--yes":
        # Run directly if --yes flag is provided
        asyncio.run(main())
    else:
        response = input("Do you want to proceed? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            asyncio.run(main())
        else:
            print("Cancelled. Use --yes flag to skip confirmation.")
            print("\nTo run this script:")
            print("  python scripts/create_fake_user_data.py --yes")
            print("\nOr set DATABASE_URL and run:")
            print("  export DATABASE_URL='postgresql://user:pass@host:port/db'")
            print("  python scripts/create_fake_user_data.py --yes")
