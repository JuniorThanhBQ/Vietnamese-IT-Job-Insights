import os
import sys
import re
import json
import time
import urllib.request
from urllib.error import URLError, HTTPError

TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = os.environ.get("GITHUB_REPOSITORY")
PR_NUMBER = os.environ.get("PR_NUMBER")

def call_api(url):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            print(f"HTTPError {e.code} for {url}. Retrying...", file=sys.stderr)
            time.sleep(2)
        except URLError as e:
            print(f"URLError {e.reason} for {url}. Retrying...", file=sys.stderr)
            time.sleep(2)
            
    print(f"Failed to fetch API after 3 attempts: {url}", file=sys.stderr)
    sys.exit(1)

def get_all_pages(base_url):
    results = []
    page = 1
    while True:
        sep = "&" if "?" in base_url else "?"
        url = f"{base_url}{sep}page={page}&per_page=100"
        data = call_api(url)
        if not data:
            break
        results.extend(data)
        if len(data) < 100:
            break
        page += 1
    return results

def detect_spam(text):
    if not text:
        return None
        
    text_no_url = re.sub(r'https?://\S+', '', text)
    
    if re.search(r'(.)\1{7,}', text_no_url, re.IGNORECASE):
        return "Repeated characters"
        
    if re.search(r'(.{3,})\1{3,}', text_no_url, re.IGNORECASE):
        return "Repeated patterns"
        
    known_smashes = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm', 'asdfasdf']
    lower_text = text_no_url.lower()
    for smash in known_smashes:
        if len(smash) >= 8 and smash in lower_text:
            return f"Keyboard sequence ({smash})"
            
    words = text_no_url.split()
    for word in words:
        if len(word) > 20:
            vowels = sum(1 for c in word.lower() if c in 'aeiouy')
            if vowels == 0:
                return "Random meaningless string (no vowels)"
                
            consonant_ratio = (len(word) - vowels) / len(word)
            if consonant_ratio > 0.9:
                return "Random meaningless string (high consonant ratio)"
                
        if re.search(r'[^aeiouy0-9\W_]{8,}', word, re.IGNORECASE):
            return "Random meaningless string (8+ consonants in a row)"
            
    return None

def main():
    print(f"Validating commits for repository: {REPO}, PR #{PR_NUMBER}\n")

    print("Fetching repository labels...")
    labels_data = get_all_pages(f"https://api.github.com/repos/{REPO}/labels")
    repo_labels = {l['name'].strip().lower(): l['name'] for l in labels_data}
    
    print("Fetching Pull Request commits...\n")
    commits_data = get_all_pages(f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/commits")
    
    has_error = False

    for commit_obj in commits_data:
        sha = commit_obj['sha']
        msg = commit_obj['commit']['message']
        
        print(f"--- Checking Commit: {sha} ---")
        print(f"Message:\n{msg}\n")
        
        parts = msg.strip().split('\n\n', 1)
        title = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ""

        match = re.match(r'^([^:]+):\s*(.+)$', title, re.DOTALL)
        if not match:
            print("Error: Invalid commit title format.")
            print("Expected structure: [Label]: Short description\n")
            has_error = True
            continue

        label_name = match.group(1).strip()
        title_desc = match.group(2).strip()

        if not title_desc:
            print("Error: Commit title content after ':' cannot be empty.\n")
            has_error = True
            continue

        if label_name.lower() not in repo_labels:
            print(f"Error: Unknown label: {label_name}\n")
            print("Available labels:")
            for valid_label in sorted(repo_labels.values()):
                print(f"- {valid_label}")
            print("")
            has_error = True
            continue

        spam_title = detect_spam(title_desc)
        if spam_title:
            print("Error: Spam detected in commit message title.\n")
            print(f"Reason:\n{spam_title}:\n{title_desc}\n")
            has_error = True
            continue

        if body:
            spam_body = detect_spam(body)
            if spam_body:
                print("Error: Spam detected in commit message body.\n")
                print(f"Reason:\n{spam_body}:\n{body[:100]}...\n")
                has_error = True
                continue

        print("-> Passed.\n")

    if has_error:
        print("Validation failed! Please fix your commit messages to proceed.")
        sys.exit(1)
    else:
        print("All commit messages passed validation.")

if __name__ == "__main__":
    main()