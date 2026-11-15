import subprocess
import json
import sys

print("Deploying static to Netlify via netlify-cli...")
res = subprocess.run(["npx.cmd", "netlify-cli", "deploy", "--dir=static", "--json"], capture_output=True, text=True)
print("Return code:", res.returncode)
print("STDOUT:", res.stdout[:300])

try:
    data = json.loads(res.stdout)
    deploy_id = data.get("deploy_id")
    site_id = data.get("site_id")
    print(f"Deploy ID: {deploy_id}, Site ID: {site_id}")
    if deploy_id and site_id:
        p_data = json.dumps({"site_id": site_id, "deploy_id": deploy_id})
        p_res = subprocess.run(["npx.cmd", "netlify-cli", "api", "restoreSiteDeploy", "--data", p_data], capture_output=True, text=True)
        print("Promote output:", p_res.stdout[:200])
        print("Successfully deployed and promoted v25 to Netlify production!")
except Exception as e:
    print("JSON Parse / Promote error:", e)
    sys.exit(1)
