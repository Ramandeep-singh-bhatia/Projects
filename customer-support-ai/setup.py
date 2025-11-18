"""
Setup script for AI Customer Support System.
"""
import subprocess
import sys
from pathlib import Path


def create_directories():
    """Create necessary data directories"""
    print("Creating data directories...")
    directories = [
        "data/documents",
        "data/vector_store",
        "data/database",
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✓ Directories created")


def setup_environment():
    """Set up environment file"""
    print("\nSetting up environment...")
    if not Path(".env").exists():
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✓ Created .env from .env.example")
            print("⚠️  Please edit .env and add your API keys:")
            print("   - ANTHROPIC_API_KEY")
            print("   - OPENAI_API_KEY")
        else:
            print("⚠️  .env.example not found")
    else:
        print("✓ .env already exists")


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    print("This may take a few minutes...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False


def initialize_database():
    """Initialize the database"""
    print("\nInitializing database...")
    try:
        from src.database import init_database
        from src.utils import get_settings

        settings = get_settings()
        init_database(settings.get_database_url())
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        return False


def main():
    """Main setup function"""
    print("=" * 60)
    print("AI CUSTOMER SUPPORT SYSTEM - SETUP")
    print("=" * 60)

    # Create directories
    create_directories()

    # Setup environment
    setup_environment()

    # Ask user if they want to install dependencies
    print("\n" + "=" * 60)
    response = input("Install Python dependencies now? (y/n): ").lower()

    if response == 'y':
        if install_dependencies():
            # Initialize database
            print("\n" + "=" * 60)
            response = input("Initialize database now? (y/n): ").lower()
            if response == 'y':
                initialize_database()

    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Edit .env and add your API keys")
    print("2. Run the FastAPI backend: uvicorn src.api.main:app --reload")
    print("3. Run the Streamlit app: streamlit run streamlit_app/app.py")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
