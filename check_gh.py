import urllib.request
import json

url = "https://api.github.com/repos/armeebaroda-cmd/gmail-whatsapp-bot/actions/runs?per_page=5"
headers = {"Authorization": "Bearer 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"}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        for run in data.get('workflow_runs', []):
            print(f"Run ID: {run['id']}, Name: {run['name']}, Status: {run['status']}, Conclusion: {run['conclusion']}, Created: {run['created_at']}")
            if run['conclusion'] == 'cancelled' or run['conclusion'] == 'failure':
                jobs_url = run['jobs_url']
                j_req = urllib.request.Request(jobs_url, headers=headers)
                with urllib.request.urlopen(j_req) as j_response:
                    j_data = json.loads(j_response.read().decode())
                    for job in j_data.get('jobs', []):
                        print(f"  Job {job['name']}: {job['conclusion']}")
                        for step in job['steps']:
                            if step['conclusion'] not in ['success', 'skipped']:
                                print(f"    Step {step['name']}: {step['conclusion']}")
except Exception as e:
    print("Error:", e)
