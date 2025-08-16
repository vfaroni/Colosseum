#!/usr/bin/env python3
"""
California Environmental Data Validator
Tower Agent - Quality Assurance Division
Mission: Validate CA environmental data meets production standards
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import glob

class CaliforniaEnvironmentalValidator:
    """Validates California environmental datasets for production readiness"""
    
    def __init__(self):
        self.base_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum")
        self.data_path = self.base_path / "data_sets" / "california"
        self.validation_results = {}
        self.validation_score = 0
        
        # Required files per county
        self.required_files = [
            "{county}_fema_flood.geojson",
            "{county}_envirostor.csv",
            "{county}_lust.csv",
            "{county}_slic.csv",
            "{county}_metadata.json",
            "README.txt"
        ]
        
        # Tier 1 Priority Counties
        self.tier1_counties = [
            "Los_Angeles", "San_Diego", "Orange", 
            "San_Francisco", "Alameda"
        ]
        
        # All 19 target counties
        self.all_counties = [
            "Los_Angeles", "San_Diego", "Orange", "San_Francisco", "Alameda",
            "Sacramento", "Contra_Costa", "Fresno", "Kern", "San_Bernardino",
            "Riverside", "Ventura", "San_Joaquin", "Sonoma", "Stanislaus",
            "Santa_Clara", "Tulare", "Santa_Barbara", "Monterey"
        ]
    
    def validate_file_presence(self, county: str) -> Dict:
        """Check if all required files exist for a county"""
        county_path = self.data_path / "CA_Environmental_Batch" / county
        results = {
            "county": county,
            "files_found": [],
            "files_missing": [],
            "validation_passed": False
        }
        
        for file_template in self.required_files:
            if "{county}" in file_template:
                filename = file_template.format(county=county)
            else:
                filename = file_template
            
            file_path = county_path / filename
            
            if file_path.exists():
                file_size = file_path.stat().st_size
                results["files_found"].append({
                    "file": filename,
                    "size": file_size,
                    "valid": file_size > 1024  # Must be > 1KB
                })
            else:
                results["files_missing"].append(filename)
        
        # Calculate validation score
        total_required = len(self.required_files)
        found_valid = len([f for f in results["files_found"] if f["valid"]])
        results["score"] = (found_valid / total_required) * 100
        results["validation_passed"] = results["score"] >= 95
        
        return results
    
    def check_record_counts(self, county: str) -> Dict:
        """Verify minimum record counts per dataset"""
        county_path = self.data_path / "CA_Environmental_Batch" / county
        counts = {
            "envirostor": 0,
            "lust": 0,
            "slic": 0,
            "fema_zones": 0
        }
        
        # Check CSV files for record counts
        for dataset in ["envirostor", "lust", "slic"]:
            csv_path = county_path / f"{county}_{dataset}.csv"
            if csv_path.exists():
                try:
                    with open(csv_path, 'r') as f:
                        # Count lines minus header
                        counts[dataset] = sum(1 for line in f) - 1
                except:
                    counts[dataset] = 0
        
        # Check GeoJSON for FEMA zones
        geojson_path = county_path / f"{county}_fema_flood.geojson"
        if geojson_path.exists():
            try:
                with open(geojson_path, 'r') as f:
                    data = json.load(f)
                    counts["fema_zones"] = len(data.get("features", []))
            except:
                counts["fema_zones"] = 0
        
        return counts
    
    def validate_metadata(self, county: str) -> Dict:
        """Validate metadata file structure and content"""
        metadata_path = self.data_path / "CA_Environmental_Batch" / county / f"{county}_metadata.json"
        
        if not metadata_path.exists():
            return {"status": "missing", "valid": False}
        
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            required_fields = ["county", "fips", "download_date", "sources"]
            missing_fields = [f for f in required_fields if f not in metadata]
            
            return {
                "status": "present",
                "valid": len(missing_fields) == 0,
                "missing_fields": missing_fields,
                "content": metadata
            }
        except Exception as e:
            return {"status": "corrupt", "valid": False, "error": str(e)}
    
    def generate_county_report(self, county: str) -> str:
        """Generate validation report for a single county"""
        report = []
        report.append(f"## {county} County Environmental Data Validation\n")
        report.append(f"**Validation Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Validator**: Tower Agent")
        
        # File validation
        file_results = self.validate_file_presence(county)
        status = "PASS" if file_results["validation_passed"] else "FAIL"
        report.append(f"**Status**: {status}\n")
        
        report.append("### File Inventory")
        for file_info in file_results["files_found"]:
            check = "✅" if file_info["valid"] else "❌"
            report.append(f"- [{check}] {file_info['file']}: {file_info['size']} bytes")
        
        for missing_file in file_results["files_missing"]:
            report.append(f"- [❌] {missing_file}: MISSING")
        
        # Record counts
        counts = self.check_record_counts(county)
        report.append("\n### Record Counts")
        report.append(f"- EnviroStor Sites: {counts['envirostor']} records")
        report.append(f"- GeoTracker LUST: {counts['lust']} records")
        report.append(f"- GeoTracker SLIC: {counts['slic']} records")
        report.append(f"- FEMA Flood Zones: {counts['fema_zones']} records")
        
        # Metadata validation
        metadata = self.validate_metadata(county)
        report.append("\n### Metadata Validation")
        if metadata["valid"]:
            report.append("- [✅] Metadata present and valid")
        else:
            report.append(f"- [❌] Metadata {metadata['status']}")
            if metadata.get("missing_fields"):
                report.append(f"  Missing fields: {', '.join(metadata['missing_fields'])}")
        
        # Quality metrics
        report.append("\n### Quality Metrics")
        report.append(f"- File Completeness: {file_results['score']:.1f}%")
        report.append(f"- Validation Score: {file_results['score']:.0f}/100")
        
        # Issues and recommendations
        if not file_results["validation_passed"]:
            report.append("\n### Issues Found")
            report.append(f"1. Missing {len(file_results['files_missing'])} required files")
            if sum(counts.values()) == 0:
                report.append("2. No environmental data records found")
            
            report.append("\n### Recommendations")
            report.append("- Re-run data acquisition for this county")
            report.append("- Check API credentials and network connectivity")
            report.append("- Verify source data availability")
        
        return "\n".join(report)
    
    def run_full_validation(self, counties: List[str] = None) -> Dict:
        """Run complete validation suite for specified counties"""
        if counties is None:
            counties = self.tier1_counties
        
        validation_summary = {
            "timestamp": datetime.now().isoformat(),
            "counties_validated": len(counties),
            "counties_passed": 0,
            "counties_failed": 0,
            "overall_score": 0,
            "county_results": {}
        }
        
        for county in counties:
            print(f"Validating {county}...")
            
            # Run validations
            file_results = self.validate_file_presence(county)
            counts = self.check_record_counts(county)
            metadata = self.validate_metadata(county)
            
            # Store results
            validation_summary["county_results"][county] = {
                "file_validation": file_results,
                "record_counts": counts,
                "metadata": metadata,
                "passed": file_results["validation_passed"]
            }
            
            if file_results["validation_passed"]:
                validation_summary["counties_passed"] += 1
            else:
                validation_summary["counties_failed"] += 1
            
            # Generate and save county report
            report = self.generate_county_report(county)
            report_path = self.base_path / "validation_reports" / f"{county}_validation.md"
            report_path.parent.mkdir(exist_ok=True)
            
            with open(report_path, 'w') as f:
                f.write(report)
        
        # Calculate overall score
        if counties:
            validation_summary["overall_score"] = (
                validation_summary["counties_passed"] / len(counties)
            ) * 100
        
        # Save summary
        summary_path = self.base_path / "validation_reports" / "validation_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(validation_summary, f, indent=2)
        
        return validation_summary
    
    def generate_strike_leader_report(self, validation_summary: Dict) -> str:
        """Generate executive summary for Strike Leader"""
        report = []
        report.append("# 🚨 CALIFORNIA ENVIRONMENTAL DATA VALIDATION REPORT\n")
        report.append(f"**Report Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Reporting Agent**: Tower - Quality Assurance Division\n")
        
        # Executive Summary
        report.append("## Executive Summary")
        
        score = validation_summary["overall_score"]
        if score >= 95:
            status = "✅ PRODUCTION READY"
            decision = "Approve for immediate production deployment"
        elif score >= 85:
            status = "⚠️ CONDITIONAL PASS"
            decision = "Deploy to staging, remediate issues within 48 hours"
        else:
            status = "❌ VALIDATION FAILED"
            decision = "Block production, return to Wingman for re-processing"
        
        report.append(f"**Overall Status**: {status}")
        report.append(f"**Validation Score**: {score:.1f}%")
        report.append(f"**Decision**: {decision}\n")
        
        # County Breakdown
        report.append("## County Validation Results")
        report.append(f"- Counties Validated: {validation_summary['counties_validated']}")
        report.append(f"- Counties Passed: {validation_summary['counties_passed']}")
        report.append(f"- Counties Failed: {validation_summary['counties_failed']}\n")
        
        # Critical Issues
        if validation_summary["counties_failed"] > 0:
            report.append("## 🔴 CRITICAL ISSUES")
            for county, results in validation_summary["county_results"].items():
                if not results["passed"]:
                    report.append(f"\n### {county} County")
                    file_val = results["file_validation"]
                    report.append(f"- Missing Files: {len(file_val['files_missing'])}")
                    report.append(f"- Validation Score: {file_val['score']:.1f}%")
                    
                    counts = results["record_counts"]
                    if sum(counts.values()) == 0:
                        report.append("- **NO DATA DOWNLOADED**")
        
        # Recommendations
        report.append("\n## Recommendations")
        if score < 85:
            report.append("1. **IMMEDIATE ACTION REQUIRED**:")
            report.append("   - Wingman to investigate download failures")
            report.append("   - Check API credentials and rate limits")
            report.append("   - Verify source website availability")
            report.append("   - Consider manual download if APIs are failing")
            report.append("\n2. **Alternative Approach**:")
            report.append("   - Use cached Texas methodology as template")
            report.append("   - Implement direct website scraping")
            report.append("   - Consider third-party data providers")
        
        # Business Impact
        report.append("\n## Business Impact")
        if score < 85:
            report.append("- ❌ $500K+ in LIHTC deals at risk without environmental data")
            report.append("- ❌ Cannot perform Phase 6 BOTN environmental screening")
            report.append("- ❌ California market penetration blocked")
        
        return "\n".join(report)


def main():
    """Main execution function"""
    print("=" * 60)
    print("CALIFORNIA ENVIRONMENTAL DATA VALIDATOR")
    print("Tower Agent - Quality Assurance Division")
    print("=" * 60)
    
    validator = CaliforniaEnvironmentalValidator()
    
    # Run validation for Tier 1 counties
    print("\nValidating Tier 1 Priority Counties...")
    validation_summary = validator.run_full_validation(validator.tier1_counties)
    
    # Generate Strike Leader report
    strike_leader_report = validator.generate_strike_leader_report(validation_summary)
    
    # Save Strike Leader report
    report_path = validator.base_path / "validation_reports" / "STRIKE_LEADER_CA_ENV_VALIDATION.md"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write(strike_leader_report)
    
    print(f"\n{'=' * 60}")
    print("VALIDATION COMPLETE")
    print(f"Overall Score: {validation_summary['overall_score']:.1f}%")
    print(f"Counties Passed: {validation_summary['counties_passed']}/{validation_summary['counties_validated']}")
    print(f"\nReports saved to: validation_reports/")
    print(f"Strike Leader Report: {report_path.name}")
    
    return validation_summary


if __name__ == "__main__":
    main()