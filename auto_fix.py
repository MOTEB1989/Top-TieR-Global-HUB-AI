# auto_fix.py (Generative AI Version)
import json
import os
import requests
import sys

# --- Configuration ---
REPORT_FILE = "reports/ultra_report.json"
PLAN_FILE   = "reports/self_heal_plan.json"
API_URL     = "http://localhost:3000/v1/ai/infer" # API Gateway to access LLM
LLM_MODEL   = "gpt-4o-mini" # The model to use for generating fixes

# --- Helper Functions ---

def safe_write(path, content):
    """Safely writes content to a file, creating directories if they don't exist."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"❌ Error writing to file {path}: {e}")
        return False

def get_ai_fix(file_path, original_code, issue_details):
    """Calls the LLM to get a generative fix for the code."""
    prompt = f"""You are an expert software engineer. Your task is to fix an issue in a source code file.
Analyze the provided code and the issue description, then rewrite the ENTIRE file with the necessary corrections.

**Rules:**
1.  Respond ONLY with the complete, raw, corrected code for the entire file.
2.  Do NOT include any explanations, comments, markdown fences (like ```python), or any text other than the code itself.
3.  Preserve the original file's structure and logic as much as possible, only changing what's necessary to fix the issue.

**File to Fix:** `{file_path}`
**Issue Found:** `{issue_details}`

**Original Code:**
---
{original_code}
---
"""
    
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a code-fixing assistant that only outputs raw code."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        print(f"🧠 Requesting AI fix for {file_path}...")
        response = requests.post(API_URL, json=payload, timeout=180) # Increased timeout
        response.raise_for_status()
        
        ai_response = response.json()
        fixed_code = ai_response['choices'][0]['message']['content']
        
        # Basic validation: ensure the response is not empty
        if not fixed_code.strip():
            print(f"⚠️ AI returned an empty response for {file_path}.")
            return None
            
        return fixed_code
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error for {file_path}: {e}")
        return None
    except (KeyError, IndexError):
        print(f"❌ Invalid AI response structure for {file_path}.")
        return None


def apply_fixes():
    """Main function to apply AI-generated fixes."""
    if not os.path.exists(REPORT_FILE) or not os.path.exists(PLAN_FILE):
        print(f"❌ Missing report ({REPORT_FILE}) or plan ({PLAN_FILE}). Cannot proceed.")
        sys.exit(1)

    with open(REPORT_FILE, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    with open(PLAN_FILE, 'r', encoding='utf-8') as f:
        plan_data = json.load(f)

    # Create a mapping from file path to its issues for quick lookup
    issues_map = {item['file']: item['issues'] for item in report_data.get('analysis_results', [])}
    
    fixes_applied_count = 0
    for fix_item in plan_data.get("recommended_fixes", []):
        file_path = fix_item.get("file")
        action = fix_item.get("suggested_action")

        if action != "autofix":
            print(f"ℹ️ Skipping manual review item: {file_path}")
            continue

        if not file_path or not os.path.exists(file_path):
            print(f"⚠️ File not found, skipping: {file_path}")
            continue
            
        # Get the specific issue details for this file
        issue_details = issues_map.get(file_path, "No specific issue details found.")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            continue

        # Get the fix from the AI
        fixed_code = get_ai_fix(file_path, original_code, issue_details)

        if fixed_code and fixed_code.strip() != original_code.strip():
            print(f"🛠️ Applying AI-generated fix to {file_path}...")
            if safe_write(file_path, fixed_code):
                fixes_applied_count += 1
                print(f"✅ Successfully updated {file_path}")
        elif fixed_code:
            print(f"✔️ No changes needed for {file_path}.")
        else:
            print(f"❌ Failed to get a valid fix for {file_path}.")

    if fixes_applied_count > 0:
        print(f"\n🎉 Generative auto-fix complete. Total files fixed: {fixes_applied_count}")
    else:
        print("\n✅ Auto-fix run complete. No files were changed.")


if __name__ == "__main__":
    apply_fixes()