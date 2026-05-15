import logging
import json
from fastapi import FastAPI, HTTPException
from gitlab_client import GitlabClient
from ai_analyzer import AIAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="GitLab MR Review API")

# Load config file
logger.info("Loading config...")
with open("../config.json", "r") as f:
    CONFIG = json.load(f)

GITLAB_URL = CONFIG["gitlab"]["url"]
GITLAB_TOKEN = CONFIG["gitlab"]["token"]
OPENAI_API_KEY = CONFIG["openai"]["api_key"]
OPENAI_BASE_URL = CONFIG["openai"].get("base_url")
PROJECTS = CONFIG["projects"]

gitlab_client = GitlabClient(GITLAB_URL, GITLAB_TOKEN)
ai_analyzer = AIAnalyzer(OPENAI_API_KEY, OPENAI_BASE_URL)
logger.info(f"Config loaded. {len(PROJECTS)} project(s) configured.")


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
    logger.info("Starting MR analysis for all projects...")
    for project in PROJECTS:
        logger.info(f"Fetching open MRs for project '{project['name']}' (id={project['id']})...")
        mrs = gitlab_client.get_open_mrs(project["id"])
        logger.info(f"Found {len(mrs)} open MR(s) in '{project['name']}'.")
        for mr in mrs:
            mr_iid = mr["iid"]
            logger.info(f"Processing MR !{mr_iid}: '{mr['title']}'")
            logger.info(f"  Fetching MR details and diffs for !{mr_iid}...")
            mr_data, mr_diff = gitlab_client.get_mr_details(project["id"], mr_iid)
            logger.info(f"  Running AI analysis for !{mr_iid}...")
            analysis = ai_analyzer.analyze_mr(mr_data, mr_diff)
            comment_body = format_review_comment(mr_data, analysis)
            logger.info(f"  Posting review comment on !{mr_iid}...")
            gitlab_client.post_mr_note(project["id"], mr_iid, comment_body)
            logger.info(f"  Review posted on !{mr_iid}.")
    logger.info("Finished analyzing all projects.")


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

    logger.info("Starting uvicorn server on 0.0.0.0:8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)