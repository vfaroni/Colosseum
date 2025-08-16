#!/usr/bin/env python3
"""
Hub-and-Spoke Regulatory Mapping Visualization
Create interactive regulatory universe mapping for demo system

Visualizes the Complete Regulatory Universe Discovery:
- Hub = State QAP (center node)
- Spokes = External regulations (connected nodes)
- Authority levels shown through node hierarchy
- Business value represented by connection strength

Built by Structured Consultants LLC
Roman Engineering Standards: Built to Last 2000+ Years
"""

import json
import math
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

@dataclass
class RegulatoryNode:
    """Individual regulatory document node"""
    node_id: str
    title: str
    authority_level: int          # 100=Federal IRC, 80=CFR, 30=State QAP
    node_type: str               # "hub", "federal_spoke", "state_spoke", "internal_spoke"
    page_count: int
    legal_ref_count: int
    business_impact_score: float  # 0-100 scale
    x_position: float = 0.0      # For visualization layout
    y_position: float = 0.0
    size: float = 10.0           # Node size for visualization

@dataclass
class RegulatoryConnection:
    """Connection between regulatory documents"""
    connection_id: str
    from_node: str              # Source node ID
    to_node: str                # Target node ID
    connection_type: str        # "reference", "cross_reference", "authority_hierarchy"
    strength: float             # 0-1 connection strength
    citation_count: int

class HubSpokeRegulatoryMapper:
    """Create hub-and-spoke regulatory universe mapping"""
    
    def __init__(self):
        self.nodes: List[RegulatoryNode] = []
        self.connections: List[RegulatoryConnection] = []
        self.jurisdictions_data = self._load_jurisdictions_data()
        
    def _load_jurisdictions_data(self) -> Dict[str, Any]:
        """Load cross-jurisdictional data if available"""
        try:
            data_path = Path(__file__).parent / "cross_jurisdictional_dashboard_data.json"
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return self._generate_sample_data()
    
    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample data for demonstration"""
        return {
            "jurisdictions": {
                "CA": {
                    "name": "California",
                    "qap_pages": 109,
                    "external_pages": 700,
                    "total_legal_refs": 316,
                    "federal_refs": 57,
                    "state_refs": 8
                },
                "FL": {
                    "name": "Florida", 
                    "qap_pages": 14,
                    "external_pages": 565,
                    "total_legal_refs": 200,
                    "federal_refs": 45,
                    "state_refs": 120
                }
            }
        }

    def create_california_hub_spoke_map(self) -> Dict[str, Any]:
        """Create detailed California hub-and-spoke mapping"""
        
        # Clear existing data
        self.nodes = []
        self.connections = []
        
        # Create central hub (CA QAP)
        ca_hub = RegulatoryNode(
            node_id="CA_QAP_HUB",
            title="California 2025 QAP",
            authority_level=30,
            node_type="hub",
            page_count=109,
            legal_ref_count=316,
            business_impact_score=95.0,
            x_position=0.0,
            y_position=0.0,
            size=50.0
        )
        self.nodes.append(ca_hub)
        
        # Create federal spokes (highest authority)
        federal_spokes = [
            {
                "id": "IRC_SECTION_42",
                "title": "IRC Section 42",
                "authority": 100,
                "pages": 45,
                "refs": 43,
                "impact": 100.0
            },
            {
                "id": "CFR_26_1_42",
                "title": "26 CFR 1.42",
                "authority": 80,
                "pages": 35,
                "refs": 13,
                "impact": 90.0
            },
            {
                "id": "PUBLIC_LAW_99_514",
                "title": "Public Law 99-514",
                "authority": 100,
                "pages": 8,
                "refs": 1,
                "impact": 85.0
            }
        ]
        
        # Position federal spokes in top tier
        for i, spoke in enumerate(federal_spokes):
            angle = (i - 1) * (2 * math.pi / 6)  # Top tier positioning
            radius = 150.0
            
            node = RegulatoryNode(
                node_id=spoke["id"],
                title=spoke["title"],
                authority_level=spoke["authority"],
                node_type="federal_spoke",
                page_count=spoke["pages"],
                legal_ref_count=spoke["refs"],
                business_impact_score=spoke["impact"],
                x_position=radius * math.cos(angle),
                y_position=radius * math.sin(angle),
                size=30.0
            )
            self.nodes.append(node)
            
            # Create connection to hub
            connection = RegulatoryConnection(
                connection_id=f"HUB_TO_{spoke['id']}",
                from_node="CA_QAP_HUB",
                to_node=spoke["id"],
                connection_type="authority_hierarchy",
                strength=0.9,
                citation_count=spoke["refs"]
            )
            self.connections.append(connection)
        
        # Create state spokes (medium authority)
        state_spokes = [
            {
                "id": "CA_HEALTH_SAFETY",
                "title": "CA Health & Safety Code",
                "authority": 30,
                "pages": 45,
                "refs": 2,
                "impact": 70.0
            },
            {
                "id": "CA_REVENUE_TAXATION",
                "title": "CA Revenue & Taxation Code",
                "authority": 30,
                "pages": 62,
                "refs": 6,
                "impact": 75.0
            },
            {
                "id": "CA_CCR_TITLE_4",
                "title": "CA CCR Title 4",
                "authority": 30,
                "pages": 320,
                "refs": 8,
                "impact": 80.0
            }
        ]
        
        # Position state spokes in middle tier
        for i, spoke in enumerate(state_spokes):
            angle = (i + 2.5) * (2 * math.pi / 6)  # Middle tier positioning
            radius = 120.0
            
            node = RegulatoryNode(
                node_id=spoke["id"],
                title=spoke["title"],
                authority_level=spoke["authority"],
                node_type="state_spoke",
                page_count=spoke["pages"],
                legal_ref_count=spoke["refs"],
                business_impact_score=spoke["impact"],
                x_position=radius * math.cos(angle),
                y_position=radius * math.sin(angle),
                size=25.0
            )
            self.nodes.append(node)
            
            # Create connection to hub
            connection = RegulatoryConnection(
                connection_id=f"HUB_TO_{spoke['id']}",
                from_node="CA_QAP_HUB",
                to_node=spoke["id"],
                connection_type="reference",
                strength=0.6,
                citation_count=spoke["refs"]
            )
            self.connections.append(connection)
        
        # Create internal reference spokes (lower authority)
        internal_spokes = [
            {
                "id": "CA_QAP_SECTION_10325",
                "title": "QAP §10325 Selection Criteria",
                "authority": 30,
                "pages": 12,
                "refs": 64,
                "impact": 60.0
            },
            {
                "id": "CA_QAP_SECTION_10322",
                "title": "QAP §10322 Application Requirements",
                "authority": 30,
                "pages": 8,
                "refs": 29,
                "impact": 55.0
            },
            {
                "id": "CA_QAP_SECTION_10327",
                "title": "QAP §10327 Financial Feasibility",
                "authority": 30,
                "pages": 6,
                "refs": 31,
                "impact": 58.0
            }
        ]
        
        # Position internal spokes in outer ring
        for i, spoke in enumerate(internal_spokes):
            angle = (i + 0.5) * (2 * math.pi / 3)  # Outer ring positioning
            radius = 90.0
            
            node = RegulatoryNode(
                node_id=spoke["id"],
                title=spoke["title"],
                authority_level=spoke["authority"],
                node_type="internal_spoke",
                page_count=spoke["pages"],
                legal_ref_count=spoke["refs"],
                business_impact_score=spoke["impact"],
                x_position=radius * math.cos(angle),
                y_position=radius * math.sin(angle),
                size=20.0
            )
            self.nodes.append(node)
            
            # Create connection to hub
            connection = RegulatoryConnection(
                connection_id=f"HUB_TO_{spoke['id']}",
                from_node="CA_QAP_HUB",
                to_node=spoke["id"],
                connection_type="cross_reference",
                strength=0.4,
                citation_count=spoke["refs"]
            )
            self.connections.append(connection)
        
        return self._export_hub_spoke_data("California")

    def create_florida_hub_spoke_map(self) -> Dict[str, Any]:
        """Create Florida hub-and-spoke mapping (extreme 40:1 ratio)"""
        
        # Clear existing data
        self.nodes = []
        self.connections = []
        
        # Create minimal hub (FL QAP)
        fl_hub = RegulatoryNode(
            node_id="FL_QAP_HUB",
            title="Florida 2025 QAP",
            authority_level=30,
            node_type="hub",
            page_count=14,
            legal_ref_count=200,
            business_impact_score=98.0,
            x_position=0.0,
            y_position=0.0,
            size=25.0  # Smaller hub relative to massive spokes
        )
        self.nodes.append(fl_hub)
        
        # Create massive external spokes (40:1 ratio demonstration)
        major_spokes = [
            {
                "id": "FL_FAC_67_21",
                "title": "FL Admin Code 67-21",
                "authority": 30,
                "pages": 145,
                "refs": 45,
                "impact": 95.0
            },
            {
                "id": "FL_FAC_67_53",
                "title": "FL Admin Code 67-53",
                "authority": 30,
                "pages": 178,
                "refs": 38,
                "impact": 92.0
            },
            {
                "id": "FL_FAC_67_48",
                "title": "FL Admin Code 67-48",
                "authority": 30,
                "pages": 134,
                "refs": 42,
                "impact": 88.0
            },
            {
                "id": "FL_FAC_67_60",
                "title": "FL Admin Code 67-60",
                "authority": 30,
                "pages": 108,
                "refs": 35,
                "impact": 85.0
            }
        ]
        
        # Position major spokes to show massive external universe
        for i, spoke in enumerate(major_spokes):
            angle = i * (2 * math.pi / 4)
            radius = 180.0  # Larger radius to show dominance
            
            node = RegulatoryNode(
                node_id=spoke["id"],
                title=spoke["title"],
                authority_level=spoke["authority"],
                node_type="state_spoke",
                page_count=spoke["pages"],
                legal_ref_count=spoke["refs"],
                business_impact_score=spoke["impact"],
                x_position=radius * math.cos(angle),
                y_position=radius * math.sin(angle),
                size=45.0  # Large spokes to show 40:1 ratio
            )
            self.nodes.append(node)
            
            # Create strong connection to tiny hub
            connection = RegulatoryConnection(
                connection_id=f"HUB_TO_{spoke['id']}",
                from_node="FL_QAP_HUB",
                to_node=spoke["id"],
                connection_type="reference",
                strength=0.95,  # Very strong connections
                citation_count=spoke["refs"]
            )
            self.connections.append(connection)
        
        return self._export_hub_spoke_data("Florida")

    def _export_hub_spoke_data(self, jurisdiction: str) -> Dict[str, Any]:
        """Export hub-spoke mapping data for visualization"""
        
        # Calculate metrics
        total_hub_pages = sum(n.page_count for n in self.nodes if n.node_type == "hub")
        total_spoke_pages = sum(n.page_count for n in self.nodes if n.node_type != "hub")
        
        ratio = total_spoke_pages / total_hub_pages if total_hub_pages > 0 else 0
        
        return {
            "jurisdiction": jurisdiction,
            "created": datetime.now().isoformat(),
            "hub_spoke_metrics": {
                "hub_pages": total_hub_pages,
                "spoke_pages": total_spoke_pages,
                "ratio": f"{ratio:.1f}:1",
                "total_nodes": len(self.nodes),
                "total_connections": len(self.connections)
            },
            "nodes": [asdict(node) for node in self.nodes],
            "connections": [asdict(conn) for conn in self.connections],
            "visualization_config": {
                "width": 800,
                "height": 600,
                "center_x": 400,
                "center_y": 300,
                "authority_colors": {
                    100: "#dc3545",  # Federal IRC - Red
                    80: "#fd7e14",   # Federal CFR - Orange  
                    60: "#ffc107",   # Federal Guidance - Yellow
                    30: "#20c997"    # State/QAP - Teal
                },
                "node_type_shapes": {
                    "hub": "circle",
                    "federal_spoke": "diamond",
                    "state_spoke": "square",
                    "internal_spoke": "triangle"
                }
            },
            "business_intelligence": {
                "revenue_opportunity": "10X+ for hub-heavy models like Florida",
                "implementation_complexity": "Low - minimal QAP processing required",
                "competitive_advantage": "Massive external universe creates high barrier to entry",
                "market_education": f"{jurisdiction} demonstrates why complete universe coverage is essential"
            }
        }

    def create_comparative_hub_spoke_analysis(self) -> Dict[str, Any]:
        """Create comparative analysis across regulatory models"""
        
        ca_data = self.create_california_hub_spoke_map()
        fl_data = self.create_florida_hub_spoke_map()
        
        comparative_analysis = {
            "analysis_type": "comparative_hub_spoke_models",
            "created": datetime.now().isoformat(),
            "jurisdictions": {
                "california": ca_data,
                "florida": fl_data
            },
            "model_comparison": {
                "california_model": {
                    "type": "Comprehensive Model",
                    "ratio": ca_data["hub_spoke_metrics"]["ratio"],
                    "characteristics": "Large QAP with moderate external references",
                    "business_value": "3-4X revenue multiplication",
                    "implementation": "Medium complexity, high value"
                },
                "florida_model": {
                    "type": "Hub-Heavy Model", 
                    "ratio": fl_data["hub_spoke_metrics"]["ratio"],
                    "characteristics": "Minimal QAP with massive external regulations",
                    "business_value": "10X+ revenue multiplication",
                    "implementation": "Low complexity, extreme value"
                }
            },
            "strategic_insights": {
                "market_opportunity": "Hub-heavy models offer highest revenue multiplication",
                "implementation_priority": "Florida-type models = quick wins, California-type = strategic value",
                "competitive_moat": "Complete universe coverage creates exponential competitive advantage",
                "customer_value": "External regulation coverage impossible for competitors to replicate quickly"
            }
        }
        
        return comparative_analysis

def main():
    """Main execution for hub-and-spoke regulatory mapping"""
    
    print("🏛️ M4 STRIKE LEADER - HUB-AND-SPOKE REGULATORY MAPPING")
    print("="*65)
    print("Mission: Visual Regulatory Universe Intelligence")
    print("Objective: Demonstrate Hub-and-Spoke Model Patterns")
    print("Business Value: 3-10X Revenue Multiplication Visualization")
    print("="*65)
    
    mapper = HubSpokeRegulatoryMapper()
    
    # Create California comprehensive model
    print("📊 Creating California Hub-and-Spoke Map (Comprehensive Model)")
    ca_mapping = mapper.create_california_hub_spoke_map()
    print(f"✅ CA Model: {ca_mapping['hub_spoke_metrics']['ratio']} ratio, {ca_mapping['hub_spoke_metrics']['total_nodes']} nodes")
    
    # Create Florida hub-heavy model
    print("📊 Creating Florida Hub-and-Spoke Map (Hub-Heavy Model)")
    fl_mapping = mapper.create_florida_hub_spoke_map()
    print(f"✅ FL Model: {fl_mapping['hub_spoke_metrics']['ratio']} ratio, {fl_mapping['hub_spoke_metrics']['total_nodes']} nodes")
    
    # Create comparative analysis
    print("📊 Creating Comparative Hub-and-Spoke Analysis")
    comparative = mapper.create_comparative_hub_spoke_analysis()
    
    # Export all mappings
    output_dir = Path(__file__).parent
    
    # Export individual mappings
    ca_path = output_dir / "ca_hub_spoke_mapping.json"
    with open(ca_path, 'w', encoding='utf-8') as f:
        json.dump(ca_mapping, f, indent=2, ensure_ascii=False)
    
    fl_path = output_dir / "fl_hub_spoke_mapping.json"
    with open(fl_path, 'w', encoding='utf-8') as f:
        json.dump(fl_mapping, f, indent=2, ensure_ascii=False)
    
    # Export comparative analysis
    comp_path = output_dir / "comparative_hub_spoke_analysis.json"
    with open(comp_path, 'w', encoding='utf-8') as f:
        json.dump(comparative, f, indent=2, ensure_ascii=False)
    
    print(f"🚀 Hub-and-Spoke Mappings Exported:")
    print(f"   📁 California: {ca_path}")
    print(f"   📁 Florida: {fl_path}")
    print(f"   📁 Comparative: {comp_path}")
    print()
    print("💰 Business Intelligence Generated:")
    print("   🎯 Visual demonstration of regulatory universe complexity")
    print("   📈 Revenue multiplication opportunity visualization")
    print("   🏆 Competitive advantage through complete universe coverage")
    print("   ⚡ Customer value proposition: 3-10X revenue increase")

if __name__ == "__main__":
    main()