#!/usr/bin/env python3
"""
🏛️ DOCLING vs LLAMA GLADIATOR COMPETITION 🏛️
Production-Focused Battle: Docling vs llama3.1:8b (vs codellama:34b backup)

Priority Order: Accuracy > Speed > Resources
"""

import time
import os
import json
import psutil
import ollama
from datetime import datetime
from docling.document_converter import DocumentConverter

class DoclingVsLlamaCompetition:
    def __init__(self):
        self.gladiators = {
            "DOCLING_CHAMPION": {
                "name": "Docling the Precise",
                "type": "docling",
                "description": "M4 Beast + IBM Docling - Pure text extraction",
                "weapon": "Advanced PDF parsing",
                "strength": "Perfect text extraction",
                "weakness": "No analysis capability"
            },
            "LLAMA_8B_SWIFT": {
                "name": "Llama 8B the Swift",
                "type": "llama",
                "model": "llama3.1:8b",
                "description": "8B parameters - Speed and efficiency",
                "weapon": "Balanced inference",
                "strength": "Analysis + reasonable speed",
                "weakness": "Limited context understanding"
            }
        }
        
        self.test_qaps = {
            "CA": "data_sets/QAP/CA/current/CA_2025_QAP_Regulations_Dec_2024.pdf",
            "TX": "data_sets/QAP/TX/current/TX_2025_QAP.pdf",
            "OR": "data_sets/QAP/OR/current/2025-qap-final.pdf"
        }
        
        self.battle_results = {}
        
    def herald_announcement(self):
        """Announce the production-focused competition"""
        print("🏛️" + "="*60 + "🏛️")
        print("   🦅 DOCLING vs LLAMA PRODUCTION BATTLE 🦅")
        print("     Accuracy > Speed > Resources")
        print("🏛️" + "="*60 + "🏛️")
        print()
        
        for gladiator, info in self.gladiators.items():
            print(f"⚔️  {info['name']} ({info.get('model', info['type'])})")
            print(f"   Strength: {info['strength']}")
            print(f"   Weakness: {info['weakness']}")
            print()
    
    def docling_extraction(self, qap_file, state):
        """Docling text extraction + basic analysis"""
        print(f"📜 Docling extracting {state} QAP...")
        
        start_time = time.time()
        start_memory = psutil.virtual_memory().used / (1024**2)
        
        try:
            converter = DocumentConverter()
            result = converter.convert(qap_file)
            text_content = result.document.export_to_markdown()
            
            end_time = time.time()
            end_memory = psutil.virtual_memory().used / (1024**2)
            
            extraction_time = end_time - start_time
            memory_used = end_memory - start_memory
            
            # Basic LIHTC accuracy assessment
            lihtc_terms = ['QAP', 'LIHTC', 'tax credit', 'qualified', 'allocation', 
                          'scoring', 'threshold', 'compliance', 'affordability', 'income',
                          'basis', 'rent', 'AMI', 'HUD', 'section 42']
            
            terms_found = sum(1 for term in lihtc_terms if term.lower() in text_content.lower())
            accuracy_score = (terms_found / len(lihtc_terms)) * 100
            
            pages = len(result.document.pages) if result.document.pages else 0
            
            result_data = {
                "extraction_time": round(extraction_time, 2),
                "memory_used": round(memory_used, 1),
                "text_length": len(text_content),
                "pages_extracted": pages,
                "lihtc_terms_found": terms_found,
                "accuracy_score": round(accuracy_score, 1),
                "chars_per_second": round(len(text_content) / extraction_time, 0),
                "pages_per_second": round(pages / extraction_time, 2),
                "sample_text": text_content[:300] + "..." if len(text_content) > 300 else text_content
            }
            
            print(f"   ✅ Extracted: {len(text_content):,} chars in {extraction_time:.2f}s")
            print(f"   🎯 LIHTC terms: {terms_found}/{len(lihtc_terms)} ({accuracy_score:.1f}%)")
            print(f"   ⚡ Speed: {pages/extraction_time:.2f} pages/sec")
            
            return result_data, None
            
        except Exception as e:
            return None, str(e)
    
    def llama_analysis(self, qap_file, model_name, state):
        """Llama model analysis of QAP document"""
        print(f"🦙 {model_name} analyzing {state} QAP...")
        
        # First extract text with Docling for fair comparison
        try:
            converter = DocumentConverter()
            result = converter.convert(qap_file)
            text_content = result.document.export_to_markdown()
        except Exception as e:
            return None, f"Text extraction failed: {e}"
        
        # Create focused LIHTC analysis prompt
        analysis_prompt = f"""
Analyze this {state} LIHTC QAP document. Provide:

1. KEY LIHTC TERMS: List specific tax credit terms found
2. SCORING CRITERIA: Main point categories for allocation
3. COMPLIANCE REQUIREMENTS: Critical regulatory requirements
4. DEADLINES: Application and compliance dates
5. AMI LIMITS: Income restrictions mentioned

Text (first 8000 chars):
{text_content[:8000]}...
"""
        
        start_time = time.time()
        start_memory = psutil.virtual_memory().used / (1024**2)
        
        try:
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            end_time = time.time()
            end_memory = psutil.virtual_memory().used / (1024**2)
            
            analysis_time = end_time - start_time
            memory_used = end_memory - start_memory
            response_text = response['message']['content']
            
            # Accuracy assessment - LIHTC term detection
            lihtc_terms = ['QAP', 'LIHTC', 'tax credit', 'qualified', 'allocation', 
                          'scoring', 'threshold', 'compliance', 'affordability', 'income',
                          'basis', 'rent', 'AMI', 'HUD', 'section 42']
            
            terms_found = sum(1 for term in lihtc_terms if term.lower() in response_text.lower())
            accuracy_score = (terms_found / len(lihtc_terms)) * 100
            
            # Analysis quality indicators
            analysis_indicators = ['scoring criteria', 'point', 'deadline', 'requirement', 
                                 'compliance', 'application', 'allocation', 'priority']
            analysis_quality = sum(1 for indicator in analysis_indicators 
                                 if indicator.lower() in response_text.lower())
            
            result_data = {
                "analysis_time": round(analysis_time, 2),
                "memory_used": round(memory_used, 1),
                "response_length": len(response_text),
                "lihtc_terms_found": terms_found,
                "accuracy_score": round(accuracy_score, 1),
                "analysis_quality": analysis_quality,
                "words_per_second": round(len(response_text.split()) / analysis_time, 2),
                "response_text": response_text[:400] + "..." if len(response_text) > 400 else response_text
            }
            
            print(f"   ⏱️  Analysis time: {analysis_time:.2f}s")
            print(f"   🎯 LIHTC accuracy: {terms_found}/{len(lihtc_terms)} ({accuracy_score:.1f}%)")
            print(f"   📊 Analysis quality: {analysis_quality}/8 indicators")
            print(f"   🚀 Speed: {result_data['words_per_second']} words/sec")
            
            return result_data, None
            
        except Exception as e:
            return None, str(e)
    
    def battle_state(self, state, qap_file):
        """Battle for one state QAP"""
        print(f"\n🏟️ BATTLE ARENA: {state} QAP")
        print("="*50)
        
        if not os.path.exists(qap_file):
            print(f"❌ Arena file not found: {qap_file}")
            return None
        
        battle_results = {
            "state": state,
            "gladiator_results": {}
        }
        
        # Docling extraction
        docling_result, docling_error = self.docling_extraction(qap_file, state)
        if docling_result:
            battle_results["gladiator_results"]["DOCLING_CHAMPION"] = docling_result
        else:
            battle_results["gladiator_results"]["DOCLING_CHAMPION"] = {"error": docling_error}
        
        # Llama 8B analysis
        llama_result, llama_error = self.llama_analysis(
            qap_file, "llama3.1:8b", state
        )
        if llama_result:
            battle_results["gladiator_results"]["LLAMA_8B_SWIFT"] = llama_result
        else:
            battle_results["gladiator_results"]["LLAMA_8B_SWIFT"] = {"error": llama_error}
        
        return battle_results
    
    def crown_champion(self, all_results):
        """Determine champion: Accuracy > Speed > Resources"""
        print(f"\n🏛️ EMPEROR'S JUDGMENT - ACCURACY FIRST!")
        print("="*60)
        
        gladiator_scores = {
            "DOCLING_CHAMPION": {"accuracy_total": 0, "speed_total": 0, "efficiency_total": 0, "battles": 0},
            "LLAMA_8B_SWIFT": {"accuracy_total": 0, "speed_total": 0, "efficiency_total": 0, "battles": 0}
        }
        
        for state, battle in all_results.items():
            print(f"\n🏟️ {state} Arena Results:")
            
            docling = battle["gladiator_results"].get("DOCLING_CHAMPION", {})
            llama = battle["gladiator_results"].get("LLAMA_8B_SWIFT", {})
            
            if "error" in docling or "error" in llama:
                print("   ⚠️  Gladiator errors - skipping comparison")
                continue
            
            # ACCURACY COMPARISON (Primary)
            docling_accuracy = docling.get("accuracy_score", 0)
            llama_accuracy = llama.get("accuracy_score", 0)
            
            if docling_accuracy > llama_accuracy:
                accuracy_winner = "DOCLING_CHAMPION"
            elif llama_accuracy > docling_accuracy:
                accuracy_winner = "LLAMA_8B_SWIFT"
            else:
                accuracy_winner = "TIE"
            
            # SPEED COMPARISON (Secondary)
            docling_speed = docling.get("pages_per_second", docling.get("chars_per_second", 0))
            llama_speed = llama.get("words_per_second", 0)
            
            # Normalize speeds (convert to relative performance)
            speed_winner = "DOCLING_CHAMPION" if docling_speed > llama_speed else "LLAMA_8B_SWIFT"
            
            # RESOURCE EFFICIENCY (Tertiary)
            docling_memory = docling.get("memory_used", 0)
            llama_memory = llama.get("memory_used", 0)
            efficiency_winner = "DOCLING_CHAMPION" if docling_memory < llama_memory else "LLAMA_8B_SWIFT"
            
            print(f"   🎯 ACCURACY: Docling {docling_accuracy}% vs Llama {llama_accuracy}% - Winner: {accuracy_winner}")
            print(f"   ⚡ SPEED: Docling {docling_speed:.1f} vs Llama {llama_speed:.1f} - Winner: {speed_winner}")
            print(f"   💾 MEMORY: Docling {docling_memory:.1f}MB vs Llama {llama_memory:.1f}MB - Winner: {efficiency_winner}")
            
            # Award points (Accuracy worth 3x, Speed 2x, Efficiency 1x)
            if accuracy_winner != "TIE":
                gladiator_scores[accuracy_winner]["accuracy_total"] += 3
            gladiator_scores[speed_winner]["speed_total"] += 2
            gladiator_scores[efficiency_winner]["efficiency_total"] += 1
            
            for gladiator in gladiator_scores:
                gladiator_scores[gladiator]["battles"] += 1
        
        # Calculate total scores
        for gladiator in gladiator_scores:
            scores = gladiator_scores[gladiator]
            scores["total_score"] = scores["accuracy_total"] + scores["speed_total"] + scores["efficiency_total"]
        
        # Crown champion
        champion = max(gladiator_scores.keys(), key=lambda x: gladiator_scores[x]["total_score"])
        
        print(f"\n👑 PRODUCTION CHAMPION: {self.gladiators[champion]['name']}!")
        print(f"   Total Score: {gladiator_scores[champion]['total_score']} points")
        print(f"   Accuracy: {gladiator_scores[champion]['accuracy_total']} points (3x weight)")
        print(f"   Speed: {gladiator_scores[champion]['speed_total']} points (2x weight)")
        print(f"   Efficiency: {gladiator_scores[champion]['efficiency_total']} points (1x weight)")
        
        return champion, gladiator_scores
    
    def conduct_production_battle(self):
        """Conduct focused production comparison"""
        self.herald_announcement()
        
        all_results = {}
        
        for state, qap_file in self.test_qaps.items():
            battle_result = self.battle_state(state, qap_file)
            if battle_result:
                all_results[state] = battle_result
        
        if all_results:
            champion, scores = self.crown_champion(all_results)
            
            # Save results
            competition_results = {
                "timestamp": datetime.now().isoformat(),
                "champion": champion,
                "scoring_priority": "Accuracy > Speed > Resources",
                "gladiator_scores": scores,
                "battle_results": all_results
            }
            
            results_file = f"docling_vs_llama_battle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(competition_results, f, indent=2)
            
            print(f"\n📜 Battle results saved: {results_file}")
            print("🏛️ Production battle complete! Ready for deployment decision!")
            
            return competition_results
        else:
            print("❌ No battles completed!")
            return None

if __name__ == "__main__":
    competition = DoclingVsLlamaCompetition()
    results = competition.conduct_production_battle()