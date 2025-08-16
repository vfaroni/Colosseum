#!/usr/bin/env python3
"""
Pipeline Manager - Pipeline Connector Integration
Roman Engineering Standard: Built for 2000+ year reliability

Integration connector for existing Colosseum pipeline systems including
CABOTN engine, email secretary, and workflow automation systems.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PipelineConnectorConfig:
    """Pipeline connector configuration"""
    cabotn_engine_path: Optional[str] = None
    email_secretary_path: Optional[str] = None
    workflow_automation_path: Optional[str] = None
    api_endpoints: Dict[str, str] = None
    enable_notifications: bool = True
    notification_webhook: Optional[str] = None
    data_sync_enabled: bool = True
    sync_interval_minutes: int = 60

@dataclass
class PipelineEvent:
    """Pipeline event for integration tracking"""
    event_id: str
    event_type: str
    source_system: str
    target_system: str
    data: Dict[str, Any]
    timestamp: str
    status: str = "pending"
    error_message: Optional[str] = None

class PipelineConnector:
    """Integration connector for Colosseum pipeline systems"""
    
    def __init__(self, config: Optional[PipelineConnectorConfig] = None):
        """Initialize pipeline connector"""
        self.config = config or self._load_default_config()
        self.system_paths = self._initialize_system_paths()
        self.api_clients = self._initialize_api_clients()
        self.event_queue: List[PipelineEvent] = []
        self.integration_status = {}
        
        logger.info("PipelineConnector initialized with Colosseum system integration")
    
    def _load_default_config(self) -> PipelineConnectorConfig:
        """Load default configuration"""
        # Derive paths relative to Colosseum root
        colosseum_root = Path(__file__).parents[4]  # Go up to Colosseum root
        
        return PipelineConnectorConfig(
            cabotn_engine_path=str(colosseum_root / "modules/lihtc_analyst/botn_engine"),
            email_secretary_path=str(colosseum_root / "modules/integration/email_management"),
            workflow_automation_path=str(colosseum_root / "modules/integration/workflow_automation"),
            api_endpoints={
                "filter_api": "http://localhost:8000/api/filter",
                "analytics_api": "http://localhost:8001/api/analytics",
                "notification_api": "http://localhost:8002/api/notify"
            },
            enable_notifications=True,
            data_sync_enabled=True
        )
    
    def _initialize_system_paths(self) -> Dict[str, Path]:
        """Initialize system paths for integration"""
        paths = {}
        
        if self.config.cabotn_engine_path:
            paths["cabotn"] = Path(self.config.cabotn_engine_path)
        
        if self.config.email_secretary_path:
            paths["email_secretary"] = Path(self.config.email_secretary_path)
        
        if self.config.workflow_automation_path:
            paths["workflow"] = Path(self.config.workflow_automation_path)
        
        # Validate paths exist
        for system, path in paths.items():
            if path.exists():
                self.integration_status[system] = "available"
                logger.info(f"System path validated: {system} -> {path}")
            else:
                self.integration_status[system] = "unavailable"
                logger.warning(f"System path not found: {system} -> {path}")
        
        return paths
    
    def _initialize_api_clients(self) -> Dict[str, Any]:
        """Initialize API clients for system integration"""
        clients = {}
        
        if self.config.api_endpoints:
            for service, endpoint in self.config.api_endpoints.items():
                try:
                    # Test API availability
                    response = requests.get(f"{endpoint}/health", timeout=5)
                    if response.status_code == 200:
                        clients[service] = endpoint
                        self.integration_status[f"{service}_api"] = "available"
                        logger.info(f"API client initialized: {service} -> {endpoint}")
                    else:
                        self.integration_status[f"{service}_api"] = "unavailable"
                        logger.warning(f"API not responding: {service} -> {endpoint}")
                except Exception as e:
                    self.integration_status[f"{service}_api"] = "error"
                    logger.warning(f"API connection failed: {service} -> {str(e)}")
        
        return clients
    
    def integrate_with_cabotn(self, extraction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate extracted data with CABOTN engine for site analysis"""
        try:
            if "cabotn" not in self.integration_status or self.integration_status["cabotn"] != "available":
                logger.warning("CABOTN engine not available for integration")
                return {"success": False, "error": "CABOTN engine unavailable"}
            
            # Extract property address for CABOTN analysis
            property_details = extraction_data.get("property_details", {})
            address = property_details.get("address")
            city = property_details.get("city")
            state = property_details.get("state")
            
            if not all([address, city, state]):
                logger.warning("Insufficient address data for CABOTN integration")
                return {"success": False, "error": "Insufficient address data"}
            
            # Prepare CABOTN input data
            cabotn_input = {
                "property_address": f"{address}, {city}, {state}",
                "analysis_type": "comprehensive",
                "include_transit": True,
                "include_environmental": True,
                "include_qct_dda": True
            }
            
            # Call CABOTN engine
            cabotn_result = self._call_cabotn_engine(cabotn_input)
            
            if cabotn_result.get("success"):
                # Merge CABOTN results with extraction data
                enhanced_data = extraction_data.copy()
                enhanced_data["cabotn_analysis"] = cabotn_result.get("analysis", {})
                
                # Record integration event
                event = PipelineEvent(
                    event_id=self._generate_event_id(),
                    event_type="cabotn_integration",
                    source_system="pipeline_manager",
                    target_system="cabotn_engine",
                    data={"property_address": cabotn_input["property_address"]},
                    timestamp=datetime.now().isoformat(),
                    status="completed"
                )
                self.event_queue.append(event)
                
                logger.info(f"CABOTN integration successful for property: {address}")
                return {"success": True, "enhanced_data": enhanced_data}
            else:
                logger.error(f"CABOTN analysis failed: {cabotn_result.get('error')}")
                return {"success": False, "error": cabotn_result.get("error")}
                
        except Exception as e:
            logger.error(f"CABOTN integration error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _call_cabotn_engine(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call CABOTN engine for site analysis"""
        try:
            cabotn_path = self.system_paths.get("cabotn")
            if not cabotn_path:
                return {"success": False, "error": "CABOTN path not configured"}
            
            # Look for main CABOTN script
            cabotn_script = cabotn_path / "src" / "main_analyzer.py"
            if not cabotn_script.exists():
                # Try alternative locations
                cabotn_script = cabotn_path / "main_analyzer.py"
                if not cabotn_script.exists():
                    return {"success": False, "error": "CABOTN script not found"}
            
            # Prepare command
            cmd = [
                "python3", str(cabotn_script),
                "--address", input_data["property_address"],
                "--analysis-type", input_data["analysis_type"],
                "--output-format", "json"
            ]
            
            if input_data.get("include_transit"):
                cmd.append("--include-transit")
            if input_data.get("include_environmental"):
                cmd.append("--include-environmental")
            if input_data.get("include_qct_dda"):
                cmd.append("--include-qct-dda")
            
            # Execute CABOTN analysis
            logger.info(f"Executing CABOTN analysis: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Parse JSON output
                analysis_result = json.loads(result.stdout)
                return {"success": True, "analysis": analysis_result}
            else:
                error_message = result.stderr or "Unknown CABOTN error"
                return {"success": False, "error": error_message}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "CABOTN analysis timeout"}
        except json.JSONDecodeError:
            return {"success": False, "error": "Invalid CABOTN output format"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def integrate_with_email_secretary(self, extraction_data: Dict[str, Any],
                                     document_path: str) -> Dict[str, Any]:
        """Integrate with email secretary for document source tracking"""
        try:
            if "email_secretary" not in self.integration_status:
                logger.warning("Email secretary not available for integration")
                return {"success": False, "error": "Email secretary unavailable"}
            
            # Check if document came from email system
            email_metadata = self._check_email_source(document_path)
            
            if email_metadata:
                # Add email source information to extraction data
                enhanced_data = extraction_data.copy()
                enhanced_data["_source_metadata"] = {
                    "source_type": "email",
                    "email_sender": email_metadata.get("sender"),
                    "email_subject": email_metadata.get("subject"),
                    "email_date": email_metadata.get("date"),
                    "email_id": email_metadata.get("email_id")
                }
                
                # Notify email secretary of successful processing
                self._notify_email_secretary({
                    "document_path": document_path,
                    "processing_status": "completed",
                    "extraction_success": True,
                    "property_name": extraction_data.get("property_details", {}).get("name")
                })
                
                logger.info(f"Email secretary integration completed for document: {Path(document_path).name}")
                return {"success": True, "enhanced_data": enhanced_data}
            else:
                logger.info("Document not from email source, skipping email secretary integration")
                return {"success": True, "enhanced_data": extraction_data}
                
        except Exception as e:
            logger.error(f"Email secretary integration error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _check_email_source(self, document_path: str) -> Optional[Dict[str, Any]]:
        """Check if document originated from email system"""
        try:
            # Look for email metadata file
            doc_path = Path(document_path)
            metadata_file = doc_path.parent / f"{doc_path.stem}_email_metadata.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            
            # Check for email patterns in file path
            path_str = str(document_path).lower()
            if any(pattern in path_str for pattern in ['email', 'inbox', 'attachments']):
                return {
                    "source_type": "email_inferred",
                    "file_path": document_path
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to check email source: {str(e)}")
            return None
    
    def _notify_email_secretary(self, notification_data: Dict[str, Any]):
        """Send notification to email secretary system"""
        try:
            secretary_path = self.system_paths.get("email_secretary")
            if not secretary_path:
                return
            
            # Create notification file
            notification_file = secretary_path / "notifications" / f"pipeline_notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            notification_file.parent.mkdir(exist_ok=True)
            
            with open(notification_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "source": "pipeline_manager",
                    "data": notification_data
                }, f, indent=2)
            
            logger.debug(f"Email secretary notification created: {notification_file}")
            
        except Exception as e:
            logger.warning(f"Failed to notify email secretary: {str(e)}")
    
    def integrate_with_workflow_automation(self, extraction_data: Dict[str, Any],
                                         processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with workflow automation system"""
        try:
            # Determine next workflow steps based on extraction data
            workflow_actions = self._determine_workflow_actions(extraction_data, processing_result)
            
            if workflow_actions:
                # Send to workflow automation system
                workflow_result = self._trigger_workflow(workflow_actions)
                
                if workflow_result.get("success"):
                    logger.info(f"Workflow automation triggered: {len(workflow_actions)} actions")
                    return {"success": True, "workflow_actions": workflow_actions}
                else:
                    logger.error(f"Workflow automation failed: {workflow_result.get('error')}")
                    return {"success": False, "error": workflow_result.get("error")}
            else:
                logger.info("No workflow actions determined for this extraction")
                return {"success": True, "workflow_actions": []}
            
        except Exception as e:
            logger.error(f"Workflow automation integration error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _determine_workflow_actions(self, extraction_data: Dict[str, Any],
                                  processing_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Determine appropriate workflow actions based on extraction data"""
        actions = []
        
        try:
            property_details = extraction_data.get("property_details", {})
            financial_metrics = extraction_data.get("financial_metrics", {})
            
            # Action: Deal scoring and categorization
            purchase_price = financial_metrics.get("purchase_price")
            cap_rate = financial_metrics.get("cap_rate")
            
            if purchase_price and cap_rate:
                actions.append({
                    "action_type": "deal_scoring",
                    "priority": "high",
                    "data": {
                        "property_name": property_details.get("name"),
                        "purchase_price": purchase_price,
                        "cap_rate": cap_rate
                    }
                })
            
            # Action: Market analysis if property location available
            if property_details.get("city") and property_details.get("state"):
                actions.append({
                    "action_type": "market_analysis",
                    "priority": "medium",
                    "data": {
                        "location": f"{property_details['city']}, {property_details['state']}",
                        "property_type": property_details.get("property_type")
                    }
                })
            
            # Action: Broker follow-up if broker information available
            transaction_details = extraction_data.get("transaction_details", {})
            if transaction_details.get("broker_email"):
                actions.append({
                    "action_type": "broker_followup",
                    "priority": "low",
                    "data": {
                        "broker_name": transaction_details.get("listing_broker"),
                        "broker_email": transaction_details.get("broker_email"),
                        "property_name": property_details.get("name")
                    }
                })
            
            # Action: Data quality review if confidence is low
            extraction_confidence = processing_result.get("confidence_score", 1.0)
            if extraction_confidence < 0.8:
                actions.append({
                    "action_type": "quality_review",
                    "priority": "high",
                    "data": {
                        "confidence_score": extraction_confidence,
                        "property_name": property_details.get("name"),
                        "review_areas": processing_result.get("warnings", [])
                    }
                })
            
            return actions
            
        except Exception as e:
            logger.error(f"Failed to determine workflow actions: {str(e)}")
            return []
    
    def _trigger_workflow(self, workflow_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Trigger workflow automation system"""
        try:
            workflow_path = self.system_paths.get("workflow")
            
            if workflow_path:
                # Create workflow file
                workflow_file = workflow_path / "incoming" / f"pipeline_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                workflow_file.parent.mkdir(exist_ok=True)
                
                with open(workflow_file, 'w') as f:
                    json.dump({
                        "timestamp": datetime.now().isoformat(),
                        "source": "pipeline_manager",
                        "actions": workflow_actions
                    }, f, indent=2)
                
                return {"success": True, "workflow_file": str(workflow_file)}
            
            # Try API endpoint if available
            workflow_api = self.api_clients.get("workflow_api")
            if workflow_api:
                response = requests.post(
                    f"{workflow_api}/trigger",
                    json={"actions": workflow_actions},
                    timeout=30
                )
                
                if response.status_code == 200:
                    return {"success": True, "api_response": response.json()}
                else:
                    return {"success": False, "error": f"API error: {response.status_code}"}
            
            return {"success": False, "error": "No workflow system available"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_notification(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Send notification through configured channels"""
        try:
            if not self.config.enable_notifications:
                return True
            
            notification = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "source": "pipeline_manager",
                "data": data
            }
            
            # Send webhook notification if configured
            if self.config.notification_webhook:
                response = requests.post(
                    self.config.notification_webhook,
                    json=notification,
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"Notification sent successfully: {event_type}")
                    return True
                else:
                    logger.warning(f"Notification webhook failed: {response.status_code}")
            
            # Log notification as fallback
            logger.info(f"Pipeline notification: {event_type} - {data}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "systems": self.integration_status.copy(),
            "event_queue_size": len(self.event_queue),
            "config": {
                "notifications_enabled": self.config.enable_notifications,
                "data_sync_enabled": self.config.data_sync_enabled,
                "sync_interval": self.config.sync_interval_minutes
            }
        }
    
    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent integration events"""
        recent_events = sorted(
            self.event_queue,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
        
        return [asdict(event) for event in recent_events]
    
    def clear_event_queue(self):
        """Clear completed events from queue"""
        self.event_queue = [
            event for event in self.event_queue 
            if event.status in ["pending", "processing"]
        ]
        logger.info("Event queue cleared of completed events")

# Example usage
if __name__ == "__main__":
    # Initialize connector
    connector = PipelineConnector()
    
    # Check integration status
    status = connector.get_integration_status()
    logger.info(f"Integration status: {status}")
    
    # Example extraction data
    sample_extraction = {
        "property_details": {
            "name": "Test Apartments",
            "address": "123 Test St",
            "city": "Austin",
            "state": "TX",
            "unit_count": 100
        },
        "financial_metrics": {
            "purchase_price": 15000000,
            "cap_rate": 0.065
        }
    }
    
    # Test CABOTN integration
    # cabotn_result = connector.integrate_with_cabotn(sample_extraction)
    # logger.info(f"CABOTN integration result: {cabotn_result.get('success')}")
    
    logger.info("PipelineConnector ready for integration")