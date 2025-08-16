#!/usr/bin/env python3
"""
🏛️ CALIFORNIA HCD HOUSING ELEMENT DATABASE INITIALIZATION
Roman Engineering Standards: Built to Last 2000+ Years
Built by Structured Consultants LLC for Colosseum Platform

Initializes PostgreSQL+PostGIS database for CA HCD Housing Element Intelligence System
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='🏛️ %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_init.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ColasseumDatabaseInitializer:
    """Initialize CA HCD Housing Element Intelligence Database"""
    
    def __init__(self, config=None):
        """Initialize with database configuration"""
        self.config = config or {
            'host': 'localhost',
            'port': 5432,
            'admin_user': 'postgres',
            'admin_password': os.getenv('POSTGRES_ADMIN_PASSWORD', ''),
            'database_name': 'ca_hcd_housing_element',
            'app_user': 'ca_hcd_user',
            'app_password': os.getenv('CA_HCD_PASSWORD', 'colosseum_hcd_2025')
        }
        
        self.schema_path = Path(__file__).parent / 'schema.sql'
        
    def create_database(self):
        """Create the main database if it doesn't exist"""
        try:
            # Connect to PostgreSQL server (not specific database)
            conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['admin_user'],
                password=self.config['admin_password'],
                database='postgres'  # Connect to default postgres database
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.config['database_name'],)
            )
            
            if cursor.fetchone():
                logger.info(f"✅ Database '{self.config['database_name']}' already exists")
            else:
                # Create database
                cursor.execute(f"CREATE DATABASE {self.config['database_name']}")
                logger.info(f"✅ Created database '{self.config['database_name']}'")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create database: {e}")
            return False
    
    def create_user(self):
        """Create application user with appropriate permissions"""
        try:
            # Connect to PostgreSQL server
            conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['admin_user'],
                password=self.config['admin_password'],
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute(
                "SELECT 1 FROM pg_user WHERE usename = %s",
                (self.config['app_user'],)
            )
            
            if cursor.fetchone():
                logger.info(f"✅ User '{self.config['app_user']}' already exists")
            else:
                # Create user
                cursor.execute(
                    f"CREATE USER {self.config['app_user']} WITH PASSWORD %s",
                    (self.config['app_password'],)
                )
                logger.info(f"✅ Created user '{self.config['app_user']}'")
            
            # Grant permissions to database
            cursor.execute(
                f"GRANT ALL PRIVILEGES ON DATABASE {self.config['database_name']} TO {self.config['app_user']}"
            )
            logger.info(f"✅ Granted database permissions to '{self.config['app_user']}'")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create user: {e}")
            return False
    
    def install_extensions(self):
        """Install required PostgreSQL extensions"""
        try:
            conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['admin_user'],
                password=self.config['admin_password'],
                database=self.config['database_name']
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            extensions = ['postgis', 'postgis_topology']
            
            for extension in extensions:
                try:
                    cursor.execute(f"CREATE EXTENSION IF NOT EXISTS {extension}")
                    logger.info(f"✅ Installed extension '{extension}'")
                except Exception as e:
                    logger.warning(f"⚠️ Could not install extension '{extension}': {e}")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to install extensions: {e}")
            return False
    
    def run_schema(self):
        """Execute the database schema SQL file"""
        try:
            if not self.schema_path.exists():
                logger.error(f"❌ Schema file not found: {self.schema_path}")
                return False
            
            # Read schema file
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Connect to the application database
            conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['admin_user'],
                password=self.config['admin_password'],
                database=self.config['database_name']
            )
            cursor = conn.cursor()
            
            # Execute schema
            cursor.execute(schema_sql)
            conn.commit()
            
            logger.info("✅ Database schema created successfully")
            
            # Grant permissions to application user
            cursor.execute(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {self.config['app_user']}")
            cursor.execute(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {self.config['app_user']}")
            cursor.execute(f"GRANT USAGE ON SCHEMA public TO {self.config['app_user']}")
            conn.commit()
            
            logger.info(f"✅ Granted table permissions to '{self.config['app_user']}'")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to run schema: {e}")
            return False
    
    def verify_installation(self):
        """Verify database installation is successful"""
        try:
            # Connect as application user
            conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['app_user'],
                password=self.config['app_password'],
                database=self.config['database_name']
            )
            cursor = conn.cursor()
            
            # Test basic queries
            cursor.execute("SELECT version()")
            postgres_version = cursor.fetchone()[0]
            logger.info(f"✅ PostgreSQL Version: {postgres_version}")
            
            cursor.execute("SELECT PostGIS_Version()")
            postgis_version = cursor.fetchone()[0]
            logger.info(f"✅ PostGIS Version: {postgis_version}")
            
            # Count tables
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            table_count = cursor.fetchone()[0]
            logger.info(f"✅ Tables created: {table_count}")
            
            # Test views
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.views 
                WHERE table_schema = 'public'
            """)
            view_count = cursor.fetchone()[0]
            logger.info(f"✅ Views created: {view_count}")
            
            # Test schema info
            cursor.execute("SELECT * FROM schema_info")
            schema_info = cursor.fetchone()
            if schema_info:
                logger.info(f"✅ Schema Info: Version {schema_info[0]}, Created {schema_info[1]}")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Database verification failed: {e}")
            return False
    
    def initialize_database(self):
        """Complete database initialization process"""
        logger.info("🏛️ STARTING CALIFORNIA HCD HOUSING ELEMENT DATABASE INITIALIZATION")
        logger.info("=" * 80)
        logger.info("📊 COLOSSEUM PLATFORM - Roman Engineering Standards")
        logger.info("🏗️ Built by Structured Consultants LLC")
        logger.info("=" * 80)
        
        steps = [
            ("Creating database", self.create_database),
            ("Creating application user", self.create_user),
            ("Installing extensions", self.install_extensions),
            ("Running schema", self.run_schema),
            ("Verifying installation", self.verify_installation)
        ]
        
        for step_name, step_function in steps:
            logger.info(f"🔄 {step_name}...")
            if not step_function():
                logger.error(f"❌ Failed at step: {step_name}")
                return False
            logger.info(f"✅ Completed: {step_name}")
        
        logger.info("=" * 80)
        logger.info("🎉 DATABASE INITIALIZATION COMPLETE!")
        logger.info("🏛️ California HCD Housing Element Intelligence Database Ready")
        logger.info(f"📊 Database: {self.config['database_name']}")
        logger.info(f"👤 User: {self.config['app_user']}")
        logger.info(f"🌐 Host: {self.config['host']}:{self.config['port']}")
        logger.info("=" * 80)
        logger.info("🎯 NEXT STEPS:")
        logger.info("   1. Run ETL pipeline to load HCD data")
        logger.info("   2. Configure intelligence algorithms")
        logger.info("   3. Launch Roman Empire dashboard")
        logger.info("=" * 80)
        
        return True

def main():
    """Main initialization function"""
    # Check for required environment variables
    if not os.getenv('POSTGRES_ADMIN_PASSWORD'):
        logger.warning("⚠️ POSTGRES_ADMIN_PASSWORD not set - you may be prompted for password")
    
    # Initialize database
    initializer = ColasseumDatabaseInitializer()
    
    if initializer.initialize_database():
        logger.info("🏛️ MISSION ACCOMPLISHED - Database ready for Roman conquest of housing data!")
        sys.exit(0)
    else:
        logger.error("❌ MISSION FAILED - Database initialization unsuccessful")
        sys.exit(1)

if __name__ == "__main__":
    main()