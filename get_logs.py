import urllib.request
import json
import zipfile
import io
import os

url = "https://api.github.com/repos/armeebaroda-cmd/gmail-whatsapp-bot/actions/runs?per_page=5"
headers = {"Authorization": "Bearer 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"}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        run = None
        for r in data.get('workflow_runs', []):
            if r['conclusion'] == 'cancelled':
                run = r
                break
        
        if run:
            logs_url = run['logs_url']
            req_logs = urllib.request.Request(logs_url, headers=headers)
            with urllib.request.urlopen(req_logs) as resp_logs:
                z = zipfile.ZipFile(io.BytesIO(resp_logs.read()))
                with open("log_output.txt", "w", encoding="utf-8") as out:
                    for name in z.namelist():
                        if "Run Gmail Telegram Summary Bot" in name:
                            out.write(f"\n--- {name} ---\n")
                            content = z.read(name).decode(errors='replace')
                            out.write(content)
except Exception as e:
    with open("log_output.txt", "w", encoding="utf-8") as out:
        out.write(f"Error: {e}")
