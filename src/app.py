from fastapi import FastAPI, HTTPException
from gitlab_client import GitlabClient
from ai_analyzer import AIAnalyzer
import json

app = FastAPI(title="GitLab MR Review API")

# Load config file
with open("../config.json", "r") as f:
    CONFIG = json.load(f)

GITLAB_URL = CONFIG["gitlab"]["url"]
GITLAB_TOKEN = CONFIG["gitlab"]["token"]
OPENAI_API_KEY = CONFIG["openai"]["api_key"]
PROJECTS = CONFIG["projects"]

gitlab_client = GitlabClient(GITLAB_URL, GITLAB_TOKEN)
ai_analyzer = AIAnalyzer(OPENAI_API_KEY)


# Format the review as markdown for the MR comment
def format_review_comment(mr_data, analysis) -> str:
    return (
        f"# Merge Request Review: {mr_data['title']}\n\n"
        f"**Analysis Summary**: {analysis['summary']}\n\n"
        f"## Positive Points\n{analysis['positives']}\n\n"
        f"## Improvement Suggestions\n{analysis['suggestions']}"
    )


# Analyze MRs for all projects
def analyze_all_projects():
    for project in PROJECTS:
        mrs = gitlab_client.get_open_mrs(project["id"])
        for mr in mrs:
            mr_data, mr_diff = gitlab_client.get_mr_details(project["id"], mr["iid"])
            analysis = ai_analyzer.analyze_mr(mr_data, mr_diff)
            comment_body = format_review_comment(mr_data, analysis)
            gitlab_client.post_mr_note(project["id"], mr_data["iid"], comment_body)


# REST API Endpoints
@app.get("/projects")
def list_projects():
    return {"projects": [{"name": p["name"], "id": p["id"]} for p in PROJECTS]}


@app.get("/projects/{project_name}/mrs")
def list_mrs(project_name: str):
    project = next((p for p in PROJECTS if p["name"] == project_name), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    mrs = gitlab_client.get_open_mrs(project["id"])
    return {"mrs": [{"iid": mr["iid"], "title": mr["title"], "web_url": mr["web_url"]} for mr in mrs]}


@app.get("/projects/{project_name}/reviews")
def list_reviews(project_name: str):
    project = next((p for p in PROJECTS if p["name"] == project_name), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    import os
    reviews = []
    output_dir = project["output_dir"]
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            if filename.endswith(".md"):
                with open(os.path.join(output_dir, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                reviews.append({"filename": filename, "content": content})
    return {"reviews": reviews}


if __name__ == "__main__":
    analyze_all_projects()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)