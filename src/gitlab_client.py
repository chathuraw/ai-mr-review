import requests

class GitlabClient:
    def __init__(self, url: str, token: str):
        self.url = url
        self.headers = {"Private-Token": token}

    def get_open_mrs(self, project_id: str):
        response = requests.get(f"{self.url}/projects/{project_id}/merge_requests?state=opened", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_mr_details(self, project_id: str, mr_iid: int):
        mr_response = requests.get(f"{self.url}/projects/{project_id}/merge_requests/{mr_iid}", headers=self.headers)
        diff_response = requests.get(f"{self.url}/projects/{project_id}/merge_requests/{mr_iid}/diffs", headers=self.headers)
        mr_response.raise_for_status()
        diff_response.raise_for_status()
        return mr_response.json(), diff_response.json()

    def post_mr_note(self, project_id: str, mr_iid: int, body: str):
        """Post a comment on a merge request.

        See: https://docs.gitlab.com/api/notes/#create-a-merge-request-note
        """
        response = requests.post(
            f"{self.url}/projects/{project_id}/merge_requests/{mr_iid}/notes",
            headers=self.headers,
            data={"body": body},
        )
        response.raise_for_status()
        return response.json()