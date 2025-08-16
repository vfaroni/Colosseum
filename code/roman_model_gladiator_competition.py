#!/usr/bin/env python3
"""
🏛️ ROMAN MODEL GLADIATOR COMPETITION 🏛️
Imperial Battle: llama3.3:70b vs llama3.1:8b

"In the Colosseum of LIHTC Processing, only the strongest model survives!"
"""

import time
import os
import json
import psutil
import ollama
from datetime import datetime
from docling.document_converter import DocumentConverter

class RomanGladiatorCompetition:
    def __init__(self):
        self.gladiators = {
            "MAXIMUS_70B": {
                "model": "llama3.3:70b",
                "title": "Maximus the Mighty",
                "description": "The 70B Champion - Raw imperial power",
                "weapon": "Massive neural networks",
                "strength": "Unmatched understanding",
                "weakness": "Resource hungry"
            },
            "SPARTACUS_8B": {
                "model": "llama3.1:8b", 
                "title": "Spartacus the Swift",
                "description": "The 8B Rebel - Speed and efficiency",
                "weapon": "Lightning fast inference",
                "strength": "Efficient processing",
                "weakness": "Limited context"
            }
        }
        
        self.arena_qaps = {
            "CA": "data_sets/QAP/CA/current/CA_2025_QAP_Regulations_Dec_2024.pdf",
            "TX": "data_sets/QAP/TX/current/TX_2025_QAP.pdf",
            "OR": "data_sets/QAP/OR/current/2025-qap-final.pdf"
        }
        
        self.battle_results = {}
        
    def herald_announcement(self):
        """Roman herald announces the competition"""
        print("🏛️" + "="*60 + "🏛️")
        print("     🦅 ROMAN MODEL GLADIATOR COMPETITION 🦅")
        print("       In the Colosseum of LIHTC Processing")
        print("🏛️" + "="*60 + "🏛️")
        print()
        
        print("📯 GLADIATORS ENTERING THE ARENA:")
        for gladiator, info in self.gladiators.items():
            print(f"⚔️  {info['title']} ({info['model']})")
            print(f"   Weapon: {info['weapon']}")
            print(f"   Strength: {info['strength']}")
            print(f"   Weakness: {info['weakness']}")
            print()
        
        print("🏟️ THE ARENA: California, Texas, Oregon QAPs")
        print("🏆 VICTORY CONDITIONS: Speed, Accuracy, Efficiency")
        print("🦁 MAY THE BEST GLADIATOR WIN!")
        print()
    
    def docling_extraction(self, qap_file):
        """Extract text using Docling (neutral ground)"""
        if not os.path.exists(qap_file):
            return None, f"Arena file not found: {qap_file}"
        
        try:
            converter = DocumentConverter()
            result = converter.convert(qap_file)
            text_content = result.document.export_to_markdown()
            return text_content, None
        except Exception as e:
            return None, str(e)
    
    def gladiator_analysis(self, gladiator_name, model_name, text_content, state):
        """Have a gladiator analyze the extracted text"""
        print(f"⚔️  {self.gladiators[gladiator_name]['title']} analyzing {state} QAP...")
        
        # Create analysis prompt
        analysis_prompt = f"""
You are analyzing a {state} LIHTC QAP document. Please provide:

1. DOCUMENT SUMMARY (2-3 sentences)
2. KEY SCORING CRITERIA (top 5 most important)  
3. LIHTC TERMS FOUND (count key regulatory terms)
4. COMPLEXITY ASSESSMENT (High/Medium/Low)
5. CRITICAL DEADLINES mentioned

Text to analyze:
{text_content[:10000]}...
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
            
            # Count LIHTC terms in response (accuracy metric)
            lihtc_terms = ['QAP', 'LIHTC', 'tax credit', 'qualified', 'allocation', 
                          'scoring', 'threshold', 'compliance', 'affordability', 'income']
            terms_found = sum(1 for term in lihtc_terms if term.lower() in response_text.lower())
            
            result = {
                "analysis_time": round(analysis_time, 2),
                "memory_used": round(memory_used, 1),
                "response_length": len(response_text),
                "lihtc_terms_found": terms_found,
                "accuracy_score": round((terms_found / len(lihtc_terms)) * 100, 1),
                "words_per_second": round(len(response_text.split()) / analysis_time, 2),
                "response_text": response_text[:500] + "..." if len(response_text) > 500 else response_text
            }
            
            print(f"   ⏱️  Analysis time: {result['analysis_time']}s")
            print(f"   🧠 LIHTC terms: {result['lihtc_terms_found']}/{len(lihtc_terms)} ({result['accuracy_score']}%)")
            print(f"   🚀 Speed: {result['words_per_second']} words/sec")
            
            return result, None
            
        except Exception as e:
            print(f"   ❌ {gladiator_name} failed: {e}")
            return None, str(e)
    
    def battle_in_arena(self, state, qap_file):
        """Conduct battle between gladiators for one QAP"""
        print(f"\n🏟️ BATTLE IN THE ARENA: {state} QAP")
        print("="*50)
        
        # First, extract text with Docling (neutral)
        print("📜 Extracting QAP text with Docling...")
        text_content, docling_error = self.docling_extraction(qap_file)
        
        if docling_error:
            print(f"❌ Arena preparation failed: {docling_error}")
            return None
        
        print(f"✅ Text extracted: {len(text_content):,} characters")
        
        battle_results = {
            "state": state,
            "text_length": len(text_content),
            "gladiator_results": {}
        }
        
        # Each gladiator analyzes the same text
        for gladiator_name, gladiator_info in self.gladiators.items():
            result, error = self.gladiator_analysis(
                gladiator_name, 
                gladiator_info["model"], 
                text_content, 
                state
            )
            
            if result:
                battle_results["gladiator_results"][gladiator_name] = result
            else:
                battle_results["gladiator_results"][gladiator_name] = {"error": error}
        
        return battle_results
    
    def crown_champion(self, all_results):
        """Determine the overall champion"""
        print("\n🏛️ ROMAN EMPEROR'S JUDGMENT")
        print("="*60)
        
        gladiator_scores = {name: {"total_score": 0, "battles_won": 0, "metrics": {}} 
                           for name in self.gladiators.keys()}
        
        # Calculate scores for each battle
        for state, battle in all_results.items():
            print(f"\n🏟️ {state} Arena Results:")
            
            valid_results = {name: result for name, result in battle["gladiator_results"].items() 
                           if "error" not in result}
            
            if len(valid_results) < 2:
                print("   ⚠️  Insufficient gladiators for comparison")
                continue
            
            # Speed competition
            fastest_time = min(r["analysis_time"] for r in valid_results.values())
            speed_winner = [name for name, r in valid_results.items() 
                          if r["analysis_time"] == fastest_time][0]
            
            # Accuracy competition  
            highest_accuracy = max(r["accuracy_score"] for r in valid_results.values())
            accuracy_winner = [name for name, r in valid_results.items() 
                             if r["accuracy_score"] == highest_accuracy][0]
            
            # Efficiency (words per second)
            highest_wps = max(r["words_per_second"] for r in valid_results.values())
            efficiency_winner = [name for name, r in valid_results.items() 
                                if r["words_per_second"] == highest_wps][0]
            
            print(f"   🏃 Speed Champion: {self.gladiators[speed_winner]['title']} ({fastest_time}s)")
            print(f"   🎯 Accuracy Champion: {self.gladiators[accuracy_winner]['title']} ({highest_accuracy}%)")
            print(f"   ⚡ Efficiency Champion: {self.gladiators[efficiency_winner]['title']} ({highest_wps} w/s)")
            
            # Award points
            winners = [speed_winner, accuracy_winner, efficiency_winner]
            for winner in winners:
                gladiator_scores[winner]["total_score"] += 1
                gladiator_scores[winner]["battles_won"] += winners.count(winner)
        
        # Crown the champion
        champion = max(gladiator_scores.keys(), key=lambda x: gladiator_scores[x]["total_score"])
        champion_info = self.gladiators[champion]
        
        print(f"\n👑 EMPEROR'S DECREE: THE CHAMPION IS...")
        print(f"🏆 {champion_info['title']} ({champion_info['model']})!")
        print(f"   Total Score: {gladiator_scores[champion]['total_score']} points")
        print(f"   Battles Won: {gladiator_scores[champion]['battles_won']}")
        
        return champion, gladiator_scores
    
    def conduct_games(self):
        """Conduct the full gladiatorial games"""
        self.herald_announcement()
        
        all_results = {}
        
        # Battle in each arena
        for state, qap_file in self.arena_qaps.items():
            battle_result = self.battle_in_arena(state, qap_file)
            if battle_result:
                all_results[state] = battle_result
        
        # Crown the champion
        if all_results:
            champion, scores = self.crown_champion(all_results)
            
            # Save results
            competition_results = {
                "timestamp": datetime.now().isoformat(),
                "champion": champion,
                "gladiator_scores": scores,
                "battle_results": all_results
            }
            
            results_file = f"roman_gladiator_competition_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(competition_results, f, indent=2)
            
            print(f"\n📜 Competition results saved: {results_file}")
            print("🏛️ The games are complete! Ave Caesar!")
            
            return competition_results
        else:
            print("❌ No battles could be completed!")
            return None

if __name__ == "__main__":
    competition = RomanGladiatorCompetition()
    results = competition.conduct_games()