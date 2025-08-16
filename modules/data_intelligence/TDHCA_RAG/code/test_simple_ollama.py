  #!/usr/bin/env python3
  import requests
  import json

  def test_ollama_directly():
      # Test if Ollama is responding
      try:
          response = requests.post(
              "http://localhost:11434/api/generate",
              json={
                  "model": "llama3.3:70b",
                  "prompt": "Extract the project name from this text: 'TDHCA Application 23461 for Estates at 
  Ferguson'. Return only JSON: {\"project_name\": \"name here\"}",
                  "stream": False,
                  "format": "json"
              },
              timeout=30
          )

          if response.status_code == 200:
              result = response.json()
              print("✅ Ollama is working!")
              print(f"Response: {result.get('response', 'No response')}")
              return True
          else:
              print(f"❌ Ollama error: {response.status_code}")
              return False

      except Exception as e:
          print(f"❌ Connection error: {e}")
          return False

  if __name__ == "__main__":
      print("🦙 Testing Ollama connection directly...")
      test_ollama_directly()
