#!/usr/bin/env python3
"""
🏛️ THREE-WAY GLADIATOR BATTLE 🏛️
Docling vs Llama 8B vs Codellama 34B
Production Decision Battle: Accuracy > Speed > Resources
"""

import time
import psutil
import ollama
from docling.document_converter import DocumentConverter

class ThreeWayGladiatorBattle:
    def __init__(self):
        self.gladiators = {
            "DOCLING_CHAMPION": {
                "name": "Docling the Precise",
                "type": "docling", 
                "description": "IBM Docling - Perfect text extraction",
                "strength": "100% accuracy, complete extraction"
            },
            "LLAMA_8B_SWIFT": {
                "name": "Llama 8B the Swift", 
                "model": "llama3.1:8b",
                "description": "8B parameters - Speed and efficiency",
                "strength": "Fast analysis, balanced performance"
            },
            "CODELLAMA_34B_MIGHTY": {
                "name": "Codellama 34B the Mighty",
                "model": "codellama:34b", 
                "description": "34B parameters - Maximum analysis power",
                "strength": "Deep understanding, comprehensive analysis"
            }
        }
        
        self.battle_results = {}
        
    def herald_announcement(self):
        """Announce the three-way battle"""
        print("🏛️" + "="*70 + "🏛️")
        print("     🦅 THREE-WAY GLADIATOR BATTLE 🦅")
        print("   Docling vs Llama 8B vs Codellama 34B")
        print("    Priority: Accuracy > Speed > Resources")
        print("🏛️" + "="*70 + "🏛️")
        print()
        
        for gladiator, info in self.gladiators.items():
            model_info = info.get('model', info.get('type', 'Unknown'))
            print(f"⚔️  {info['name']} ({model_info})")
            print(f"   Strength: {info['strength']}")
            print()
    
    def test_docling(self):
        """Test Docling extraction"""
        print("📜 DOCLING CHAMPION - CA QAP Processing")
        print("="*45)
        
        qap_file = "data_sets/QAP/CA/current/CA_2025_QAP_Regulations_Dec_2024.pdf"
        
        start_time = time.time()
        start_memory = psutil.virtual_memory().used / (1024**2)
        
        try:
            converter = DocumentConverter()
            result = converter.convert(qap_file)
            text_content = result.document.export_to_markdown()
            
            end_time = time.time()
            end_memory = psutil.virtual_memory().used / (1024**2)
            
            processing_time = end_time - start_time
            memory_used = end_memory - start_memory
            pages = len(result.document.pages) if result.document.pages else 0
            
            # LIHTC accuracy test
            lihtc_terms = ['QAP', 'LIHTC', 'tax credit', 'qualified', 'allocation', 
                          'scoring', 'threshold', 'compliance', 'affordability', 'income',
                          'basis', 'rent', 'AMI', 'HUD', 'section 42']
            
            terms_found = sum(1 for term in lihtc_terms if term.lower() in text_content.lower())
            accuracy_score = (terms_found / len(lihtc_terms)) * 100
            
            print(f"✅ DOCLING RESULTS:")
            print(f"   ⏱️  Time: {processing_time:.2f}s")
            print(f"   💾 Memory: {memory_used:.1f}MB")
            print(f"   📄 Pages: {pages}")
            print(f"   📝 Text: {len(text_content):,} chars")
            print(f"   🎯 LIHTC Accuracy: {terms_found}/{len(lihtc_terms)} ({accuracy_score:.1f}%)")
            print(f"   ⚡ Speed: {pages/processing_time:.2f} pages/sec")
            
            return {
                "name": "Docling",
                "time": processing_time,
                "memory": memory_used,
                "pages": pages,
                "text_length": len(text_content),
                "accuracy": accuracy_score,
                "terms_found": terms_found,
                "type": "extraction",
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Docling failed: {e}")
            return {"name": "Docling", "success": False, "error": str(e)}
    
    def test_llama_model(self, model_name, gladiator_name):
        """Test a Llama model"""
        print(f"\n🦙 {gladiator_name.upper()} - LIHTC Analysis Test")
        print("="*45)
        
        # Standard LIHTC knowledge test
        test_prompt = """
Analyze LIHTC (Low-Income Housing Tax Credit) QAP requirements. Provide:

1. KEY ALLOCATION CRITERIA: Main scoring categories for tax credit allocation
2. COMPLIANCE REQUIREMENTS: Critical federal and state requirements  
3. INCOME LIMITS: AMI restrictions and tenant qualification rules
4. DEADLINES: Application and compliance timeline requirements
5. BASIS CALCULATION: Qualified basis and eligible costs overview

Keep response comprehensive but under 400 words.
"""
        
        start_time = time.time()
        start_memory = psutil.virtual_memory().used / (1024**2)
        
        try:
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": test_prompt}]
            )
            
            end_time = time.time()
            end_memory = psutil.virtual_memory().used / (1024**2)
            
            analysis_time = end_time - start_time
            memory_used = end_memory - start_memory
            response_text = response['message']['content']
            
            # LIHTC accuracy test
            lihtc_terms = ['QAP', 'LIHTC', 'tax credit', 'qualified', 'allocation', 
                          'scoring', 'threshold', 'compliance', 'affordability', 'income',
                          'basis', 'rent', 'AMI', 'HUD', 'section 42']
            
            terms_found = sum(1 for term in lihtc_terms if term.lower() in response_text.lower())
            accuracy_score = (terms_found / len(lihtc_terms)) * 100
            
            # Analysis quality - specific LIHTC concepts
            quality_terms = ['allocation plan', 'scoring criteria', 'set aside', 'compliance period',
                           'placed in service', 'qualified census tract', 'difficult development area',
                           'maximum rent', 'income certification', 'recapture']
            quality_found = sum(1 for term in quality_terms if term.lower() in response_text.lower())
            quality_score = (quality_found / len(quality_terms)) * 100
            
            print(f"✅ {gladiator_name.upper()} RESULTS:")
            print(f"   ⏱️  Time: {analysis_time:.2f}s") 
            print(f"   💾 Memory: {memory_used:.1f}MB")
            print(f"   📝 Response: {len(response_text)} chars")
            print(f"   🎯 LIHTC Accuracy: {terms_found}/{len(lihtc_terms)} ({accuracy_score:.1f}%)")
            print(f"   📊 Quality Score: {quality_found}/{len(quality_terms)} ({quality_score:.1f}%)")
            print(f"   ⚡ Speed: {len(response_text.split())/analysis_time:.1f} words/sec")
            
            # Show sample response
            print(f"\n📖 Sample Response:")
            sample = response_text[:200] + "..." if len(response_text) > 200 else response_text
            print(sample)
            
            return {
                "name": gladiator_name,
                "model": model_name,
                "time": analysis_time,
                "memory": memory_used,
                "response_length": len(response_text),
                "accuracy": accuracy_score,
                "quality": quality_score,
                "terms_found": terms_found,
                "quality_found": quality_found,
                "words_per_sec": len(response_text.split()) / analysis_time,
                "type": "analysis",
                "success": True,
                "response_sample": response_text[:300] + "..." if len(response_text) > 300 else response_text
            }
            
        except Exception as e:
            print(f"❌ {gladiator_name} failed: {e}")
            return {"name": gladiator_name, "model": model_name, "success": False, "error": str(e)}
    
    def compare_three_gladiators(self, docling_result, llama8b_result, codellama34b_result):
        """Compare all three approaches"""
        print("\n🏛️ EMPEROR'S THREE-WAY JUDGMENT")
        print("="*60)
        
        results = [docling_result, llama8b_result, codellama34b_result]
        successful_results = [r for r in results if r.get('success', False)]
        
        if len(successful_results) < 3:
            print("❌ Not all gladiators completed successfully")
            for result in results:
                if not result.get('success', False):
                    print(f"   {result['name']}: {result.get('error', 'Unknown error')}")
            return
        
        print("🎯 ACCURACY COMPARISON (Priority #1):")
        for result in successful_results:
            if result['type'] == 'extraction':
                print(f"   {result['name']}: {result['accuracy']:.1f}% (Text extraction accuracy)")
            else:
                print(f"   {result['name']}: {result['accuracy']:.1f}% + {result['quality']:.1f}% quality")
        
        # For accuracy, consider both term detection and analysis quality for LLMs
        docling_acc = docling_result['accuracy']
        llama8b_acc = llama8b_result['accuracy'] + (llama8b_result['quality'] * 0.5)  # Weight quality
        codellama34b_acc = codellama34b_result['accuracy'] + (codellama34b_result['quality'] * 0.5)
        
        accuracy_scores = {
            "Docling": docling_acc,
            "Llama 8B": llama8b_acc, 
            "Codellama 34B": codellama34b_acc
        }
        accuracy_winner = max(accuracy_scores.keys(), key=lambda x: accuracy_scores[x])
        print(f"   🏆 Accuracy Winner: {accuracy_winner}")
        
        print("\n⚡ SPEED COMPARISON (Priority #2):")
        for result in successful_results:
            print(f"   {result['name']}: {result['time']:.2f}s")
        
        speed_scores = {r['name']: r['time'] for r in successful_results}
        speed_winner = min(speed_scores.keys(), key=lambda x: speed_scores[x])  # Fastest = lowest time
        print(f"   🏆 Speed Winner: {speed_winner}")
        
        print("\n💾 RESOURCE USAGE (Priority #3):")
        for result in successful_results:
            print(f"   {result['name']}: {result['memory']:.1f}MB")
        
        memory_scores = {r['name']: r['memory'] for r in successful_results}
        resource_winner = min(memory_scores.keys(), key=lambda x: memory_scores[x])  # Most efficient = lowest memory
        print(f"   🏆 Resource Winner: {resource_winner}")
        
        # Calculate overall scores (Accuracy: 3pts, Speed: 2pts, Resources: 1pt)
        final_scores = {"Docling": 0, "Llama 8B": 0, "Codellama 34B": 0}
        
        # Award points
        if accuracy_winner in final_scores:
            final_scores[accuracy_winner] += 3
        if speed_winner in final_scores:
            final_scores[speed_winner] += 2  
        if resource_winner in final_scores:
            final_scores[resource_winner] += 1
        
        overall_winner = max(final_scores.keys(), key=lambda x: final_scores[x])
        
        print(f"\n👑 OVERALL PRODUCTION CHAMPION: {overall_winner}")
        print("Final Scoring (Accuracy=3pts, Speed=2pts, Resources=1pt):")
        for gladiator, score in final_scores.items():
            print(f"   {gladiator}: {score}/6 points")
        
        return {
            "accuracy_winner": accuracy_winner,
            "speed_winner": speed_winner, 
            "resource_winner": resource_winner,
            "overall_winner": overall_winner,
            "final_scores": final_scores,
            "detailed_results": successful_results
        }
    
    def conduct_three_way_battle(self):
        """Execute the complete three-way battle"""
        self.herald_announcement()
        
        # Test all three gladiators
        print("🚀 BEGINNING THREE-WAY BATTLE...")
        
        docling_result = self.test_docling()
        llama8b_result = self.test_llama_model("llama3.1:8b", "Llama 8B")
        codellama34b_result = self.test_llama_model("codellama:34b", "Codellama 34B")
        
        # Compare results
        comparison = self.compare_three_gladiators(docling_result, llama8b_result, codellama34b_result)
        
        return {
            "docling": docling_result,
            "llama8b": llama8b_result, 
            "codellama34b": codellama34b_result,
            "comparison": comparison
        }

if __name__ == "__main__":
    battle = ThreeWayGladiatorBattle()
    results = battle.conduct_three_way_battle()