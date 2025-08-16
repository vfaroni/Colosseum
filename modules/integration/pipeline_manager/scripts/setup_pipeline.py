#!/usr/bin/env python3
"""
Pipeline Manager - Setup and Configuration Script
Roman Engineering Standard: Built for 2000+ year reliability

Interactive setup script for configuring the Pipeline Manager system
including API keys, Excel templates, and system verification.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import getpass

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from integrations.openai_client import OpenAIClient, OpenAIConfig
from core.excel_manager import ExcelManager, ExcelConfig
from core.data_validator import DataValidator
from integrations.pipeline_connector import PipelineConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Setup and configure the Pipeline Manager system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 setup_pipeline.py --interactive
  python3 setup_pipeline.py --config-file pipeline_config.json
  python3 setup_pipeline.py --verify-only
  python3 setup_pipeline.py --create-excel-template pipeline.xlsx
  python3 setup_pipeline.py --test-api-key
        """
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run interactive setup wizard"
    )
    
    parser.add_argument(
        "--config-file",
        help="Configuration file to create/update"
    )
    
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing configuration"
    )
    
    parser.add_argument(
        "--create-excel-template",
        help="Create Excel template file at specified path"
    )
    
    parser.add_argument(
        "--test-api-key",
        action="store_true",
        help="Test OpenAI API key"
    )
    
    parser.add_argument(
        "--install-dependencies",
        action="store_true",
        help="Install required Python dependencies"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser


def print_banner():
    """Print setup banner"""
    banner = """
🏛️ ═══════════════════════════════════════════════════════════════════════════ 🏛️
                        PIPELINE MANAGER SETUP WIZARD
                   Roman Engineering Standard: Built for 2000+ Years
🏛️ ═══════════════════════════════════════════════════════════════════════════ 🏛️

Welcome to the Pipeline Manager setup wizard. This script will help you configure
the AI-powered document processing system for real estate investment analysis.

Features being configured:
• OpenAI GPT-4 API integration for document extraction
• Excel pipeline template creation and formatting
• Data validation rules and quality assurance
• Integration with existing Colosseum systems
• Performance monitoring and error handling

Let's build something that lasts 2000+ years! 🏗️
"""
    print(banner)


def check_prerequisites() -> bool:
    """Check system prerequisites"""
    logger.info("🔍 Checking system prerequisites...")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append(f"Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
    else:
        logger.info(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check required packages
    required_packages = [
        ("openai", "OpenAI API client"),
        ("openpyxl", "Excel file processing"),
        ("pandas", "Data analysis"),
        ("PyPDF2", "PDF processing"),
        ("python-docx", "Word document processing"),
        ("python-pptx", "PowerPoint processing"),
        ("requests", "HTTP requests")
    ]
    
    missing_packages = []
    for package, description in required_packages:
        try:
            __import__(package.replace("-", "_"))
            logger.info(f"✅ {package}: {description}")
        except ImportError:
            missing_packages.append(package)
            issues.append(f"Missing package: {package} ({description})")
    
    # Check write permissions in current directory
    test_file = Path("test_write_permissions.tmp")
    try:
        test_file.write_text("test")
        test_file.unlink()
        logger.info("✅ Write permissions: Current directory")
    except Exception as e:
        issues.append(f"No write permissions in current directory: {e}")
    
    if issues:
        logger.error("❌ Prerequisites check failed:")
        for issue in issues:
            logger.error(f"   - {issue}")
        
        if missing_packages:
            logger.info("\n💡 To install missing packages, run:")
            logger.info(f"   pip install {' '.join(missing_packages)}")
        
        return False
    
    logger.info("✅ All prerequisites satisfied")
    return True


def interactive_setup() -> Dict[str, Any]:
    """Run interactive setup wizard"""
    logger.info("🎯 Starting interactive configuration...")
    
    config = {
        "pipeline_manager": {
            "version": "1.0.0",
            "created_at": "",
            "openai": {},
            "excel": {},
            "validation": {},
            "integration": {},
            "performance": {}
        }
    }
    
    # OpenAI Configuration
    print("\n📡 OpenAI API Configuration")
    print("=" * 40)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ Found OPENAI_API_KEY environment variable")
        use_env_key = input("Use existing environment variable? (Y/n): ").strip().lower()
        if use_env_key in ['', 'y', 'yes']:
            config["pipeline_manager"]["openai"]["use_env_key"] = True
        else:
            api_key = getpass.getpass("Enter OpenAI API key: ")
            config["pipeline_manager"]["openai"]["api_key"] = api_key
    else:
        print("❌ OPENAI_API_KEY environment variable not found")
        choice = input("Enter API key now or set environment variable? (enter/env): ").strip().lower()
        
        if choice in ['', 'enter']:
            api_key = getpass.getpass("Enter OpenAI API key: ")
            config["pipeline_manager"]["openai"]["api_key"] = api_key
        else:
            print("💡 Please set OPENAI_API_KEY environment variable and run setup again")
            return {}
    
    # Model selection
    models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"]
    print(f"\nAvailable models: {', '.join(models)}")
    model = input("Select model (default: gpt-4): ").strip() or "gpt-4"
    if model not in models:
        logger.warning(f"Unknown model '{model}', using gpt-4")
        model = "gpt-4"
    config["pipeline_manager"]["openai"]["model"] = model
    
    # Temperature setting
    try:
        temperature = float(input("Model temperature (0.0-2.0, default: 0.1): ").strip() or "0.1")
        temperature = max(0.0, min(2.0, temperature))
    except ValueError:
        temperature = 0.1
    config["pipeline_manager"]["openai"]["temperature"] = temperature
    
    # Excel Configuration
    print("\n📊 Excel Pipeline Configuration")
    print("=" * 40)
    
    excel_file = input("Excel pipeline file path (default: pipeline.xlsx): ").strip() or "pipeline.xlsx"
    config["pipeline_manager"]["excel"]["file_path"] = excel_file
    
    sheet_name = input("Worksheet name (default: Deal Pipeline): ").strip() or "Deal Pipeline"
    config["pipeline_manager"]["excel"]["sheet_name"] = sheet_name
    
    backup_enabled = input("Enable automatic backups? (Y/n): ").strip().lower() in ['', 'y', 'yes']
    config["pipeline_manager"]["excel"]["backup_enabled"] = backup_enabled
    
    # Processing Configuration
    print("\n⚙️ Processing Configuration") 
    print("=" * 40)
    
    try:
        max_workers = int(input("Maximum concurrent workers (default: 4): ").strip() or "4")
        max_workers = max(1, min(16, max_workers))
    except ValueError:
        max_workers = 4
    config["pipeline_manager"]["processing"] = {"max_concurrent_tasks": max_workers}
    
    try:
        timeout = int(input("Processing timeout in seconds (default: 300): ").strip() or "300")
        timeout = max(60, min(1800, timeout))
    except ValueError:
        timeout = 300
    config["pipeline_manager"]["processing"]["timeout_seconds"] = timeout
    
    # Validation Configuration
    print("\n✅ Validation Configuration")
    print("=" * 40)
    
    strict_mode = input("Enable strict validation mode? (y/N): ").strip().lower() in ['y', 'yes']
    config["pipeline_manager"]["validation"]["strict_mode"] = strict_mode
    
    auto_correct = input("Enable automatic data correction? (Y/n): ").strip().lower() in ['', 'y', 'yes']
    config["pipeline_manager"]["validation"]["auto_correct"] = auto_correct
    
    try:
        confidence_threshold = float(input("Confidence threshold (0.0-1.0, default: 0.85): ").strip() or "0.85")
        confidence_threshold = max(0.0, min(1.0, confidence_threshold))
    except ValueError:
        confidence_threshold = 0.85
    config["pipeline_manager"]["validation"]["confidence_threshold"] = confidence_threshold
    
    # Integration Options
    print("\n🔗 System Integration")
    print("=" * 40)
    
    enable_cabotn = input("Enable CABOTN engine integration? (Y/n): ").strip().lower() in ['', 'y', 'yes']
    enable_email = input("Enable email secretary integration? (Y/n): ").strip().lower() in ['', 'y', 'yes']
    enable_workflow = input("Enable workflow automation? (Y/n): ").strip().lower() in ['', 'y', 'yes']
    
    config["pipeline_manager"]["integration"] = {
        "cabotn_enabled": enable_cabotn,
        "email_secretary_enabled": enable_email,
        "workflow_automation_enabled": enable_workflow
    }
    
    # Performance Monitoring
    print("\n📈 Performance Monitoring")
    print("=" * 40)
    
    enable_metrics = input("Enable performance metrics collection? (Y/n): ").strip().lower() in ['', 'y', 'yes']
    enable_logging = input("Enable detailed processing logs? (Y/n): ").strip().lower() in ['', 'y', 'yes']
    
    config["pipeline_manager"]["performance"] = {
        "enable_metrics": enable_metrics,
        "log_processing_details": enable_logging,
        "save_performance_data": True
    }
    
    # Finalize configuration
    from datetime import datetime
    config["pipeline_manager"]["created_at"] = datetime.now().isoformat()
    
    logger.info("✅ Interactive configuration completed")
    return config


def verify_configuration(config: Dict[str, Any]) -> bool:
    """Verify configuration by testing components"""
    logger.info("🔍 Verifying configuration...")
    
    pipeline_config = config.get("pipeline_manager", {})
    verification_results = []
    
    # Test OpenAI API
    try:
        logger.info("Testing OpenAI API connection...")
        
        openai_config = pipeline_config.get("openai", {})
        api_key = openai_config.get("api_key") or os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            verification_results.append("❌ OpenAI API key not found")
        else:
            client_config = OpenAIConfig(
                api_key=api_key,
                model=openai_config.get("model", "gpt-4"),
                temperature=openai_config.get("temperature", 0.1)
            )
            
            client = OpenAIClient(client_config)
            if client.validate_api_key():
                verification_results.append("✅ OpenAI API connection successful")
            else:
                verification_results.append("❌ OpenAI API key validation failed")
    
    except Exception as e:
        verification_results.append(f"❌ OpenAI API test error: {str(e)}")
    
    # Test Excel functionality
    try:
        logger.info("Testing Excel functionality...")
        
        excel_config = pipeline_config.get("excel", {})
        test_file = "test_excel_verification.xlsx"
        
        excel_manager_config = ExcelConfig(
            file_path=test_file,
            sheet_name=excel_config.get("sheet_name", "Test"),
            backup_enabled=False
        )
        
        excel_manager = ExcelManager(excel_manager_config)
        
        # Test basic operations
        headers = ["Test Column 1", "Test Column 2"]
        if excel_manager.create_workbook(test_file):
            if excel_manager.create_worksheet("Test", headers):
                if excel_manager.save_workbook():
                    verification_results.append("✅ Excel functionality working")
                    # Clean up
                    Path(test_file).unlink(missing_ok=True)
                else:
                    verification_results.append("❌ Excel save failed")
            else:
                verification_results.append("❌ Excel worksheet creation failed")
        else:
            verification_results.append("❌ Excel workbook creation failed")
    
    except Exception as e:
        verification_results.append(f"❌ Excel test error: {str(e)}")
    
    # Test data validator
    try:
        logger.info("Testing data validation...")
        
        validator = DataValidator()
        test_data = {
            "property_details": {
                "name": "Test Property",
                "address": "123 Test St",
                "city": "Test City",
                "state": "TX",
                "unit_count": 100
            }
        }
        
        result = validator.validate_extraction(test_data)
        if result.is_valid:
            verification_results.append("✅ Data validation working")
        else:
            verification_results.append("⚠️ Data validation has issues (check configuration)")
    
    except Exception as e:
        verification_results.append(f"❌ Data validation test error: {str(e)}")
    
    # Test system integrations
    try:
        logger.info("Testing system integrations...")
        
        connector = PipelineConnector()
        status = connector.get_integration_status()
        
        if status:
            available_systems = sum(1 for s in status["systems"].values() if s == "available")
            total_systems = len(status["systems"])
            verification_results.append(f"ℹ️ System integrations: {available_systems}/{total_systems} available")
        else:
            verification_results.append("⚠️ System integration status unavailable")
    
    except Exception as e:
        verification_results.append(f"❌ Integration test error: {str(e)}")
    
    # Display results
    logger.info("\n🎯 Verification Results:")
    for result in verification_results:
        logger.info(f"   {result}")
    
    # Determine overall success
    failed_tests = [r for r in verification_results if r.startswith("❌")]
    if failed_tests:
        logger.error(f"\n❌ Verification failed: {len(failed_tests)} issues found")
        return False
    else:
        logger.info("\n✅ All verification tests passed")
        return True


def create_excel_template(file_path: str) -> bool:
    """Create Excel template with proper formatting"""
    logger.info(f"📊 Creating Excel template: {file_path}")
    
    try:
        # Load schema
        schema_path = Path(__file__).parent.parent / "templates" / "excel_schemas" / "default_pipeline_schema.json"
        
        if not schema_path.exists():
            logger.error("Excel schema template not found")
            return False
        
        with open(schema_path) as f:
            schema = json.load(f)
        
        # Create Excel manager
        config = ExcelConfig(
            file_path=file_path,
            sheet_name=schema.get("worksheet_settings", {}).get("sheet_name", "Deal Pipeline"),
            backup_enabled=False
        )
        
        excel_manager = ExcelManager(config)
        
        # Extract headers and column widths from schema
        columns = schema.get("columns", [])
        headers = [col["column_name"] for col in columns]
        column_widths = {col["column_name"]: col.get("formatting", {}).get("width", 15) for col in columns}
        
        # Create workbook and worksheet
        if excel_manager.create_workbook(file_path):
            if excel_manager.create_worksheet(schema.get("worksheet_settings", {}).get("sheet_name", "Deal Pipeline"), headers, column_widths):
                if excel_manager.save_workbook():
                    logger.info(f"✅ Excel template created successfully: {file_path}")
                    
                    # Display template info
                    stats = excel_manager.get_worksheet_statistics(config.sheet_name)
                    logger.info(f"   📋 Template: {stats.get('total_columns', 0)} columns, ready for data")
                    logger.info(f"   📊 Schema: {schema.get('schema_name', 'default')} v{schema.get('version', '1.0')}")
                    
                    return True
    
    except Exception as e:
        logger.error(f"Failed to create Excel template: {e}")
    
    return False


def install_dependencies() -> bool:
    """Install required Python dependencies"""
    logger.info("📦 Installing required dependencies...")
    
    requirements = [
        "openai>=1.0.0",
        "openpyxl>=3.0.0",
        "pandas>=1.3.0",
        "PyPDF2>=3.0.0",
        "python-docx>=0.8.0",
        "python-pptx>=0.6.0",
        "requests>=2.25.0"
    ]
    
    try:
        import subprocess
        
        for package in requirements:
            logger.info(f"Installing {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ {package} installed successfully")
            else:
                logger.error(f"❌ Failed to install {package}: {result.stderr}")
                return False
        
        logger.info("✅ All dependencies installed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Dependency installation failed: {e}")
        return False


def save_configuration(config: Dict[str, Any], file_path: str) -> bool:
    """Save configuration to file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2, default=str)
        
        logger.info(f"✅ Configuration saved to: {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
        return False


def main():
    """Main execution function"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print banner
    if args.interactive:
        print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        if args.install_dependencies:
            if not install_dependencies():
                sys.exit(1)
            logger.info("Dependencies installed. Please run setup again.")
            sys.exit(0)
        else:
            logger.info("💡 Use --install-dependencies to install missing packages")
            sys.exit(1)
    
    # Handle specific actions
    if args.test_api_key:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            sys.exit(1)
        
        client = OpenAIClient(OpenAIConfig(api_key=api_key))
        if client.validate_api_key():
            logger.info("✅ OpenAI API key is valid")
        else:
            logger.error("❌ OpenAI API key validation failed")
            sys.exit(1)
        return
    
    if args.create_excel_template:
        if create_excel_template(args.create_excel_template):
            logger.info("✅ Excel template creation completed")
        else:
            logger.error("❌ Excel template creation failed")
            sys.exit(1)
        return
    
    # Interactive setup
    if args.interactive:
        config = interactive_setup()
        if not config:
            logger.error("❌ Interactive setup cancelled")
            sys.exit(1)
        
        # Save configuration
        config_file = args.config_file or "pipeline_config.json"
        if not save_configuration(config, config_file):
            sys.exit(1)
        
        # Verify configuration
        if not verify_configuration(config):
            logger.warning("⚠️ Configuration verification failed - please review settings")
    
    # Verification only
    elif args.verify_only:
        config_file = args.config_file or "pipeline_config.json"
        
        if not Path(config_file).exists():
            logger.error(f"Configuration file not found: {config_file}")
            sys.exit(1)
        
        try:
            with open(config_file) as f:
                config = json.load(f)
            
            if verify_configuration(config):
                logger.info("✅ Configuration verification successful")
            else:
                logger.error("❌ Configuration verification failed")
                sys.exit(1)
        
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    
    else:
        # Show help if no specific action
        parser.print_help()
    
    logger.info("🏛️ Pipeline Manager setup completed successfully")


if __name__ == "__main__":
    main()