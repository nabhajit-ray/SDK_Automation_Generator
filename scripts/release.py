import requests
#headers = {'Authorization': 'token {}'.format('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')}
#api_url = 'https://api.github.com/repos/chebroluharika/SDK_Automation_Generator/releases'
#req = requests.post(api_url,
#                   json={'tag_name': 'v0.0.1'},
#                   headers=headers)
#print(req.json())

def create_draft_release(release, user, repo, token):
    api_url = 'https://api.github.com/repos/{user}/{repo}/releases'
    api_url = api_url.format(user=user, repo=repo)

    def get_release_json():
        tag_url = api_url + '/tags/{release}'.format(release=release)
        req = requests.get(tag_url)
        release_json = req.json()
        if ('message' in release_json and
                release_json['message'] == 'Not Found'):
            return False
        return release_json

    release_json = get_release_json()

    if not release_json:
        headers = {'Authorization': 'token {}'.format(token)}
        req = requests.post(api_url,
                            json={'tag_name': release, 'draft': True, 'name': release, 'body': 'See the CHANGELOG for details'},
                            headers=headers)
        req.raise_for_status()
        release_json = get_release_json()
        for wait in (1, 1, 2, 2, 5, 5, 10, 10, 10, 30, 60, 120):
            if release_json:
                break
            print(f"Release not found on GitHub. Trying again in {wait} second(s).")
            print(f"    It should appear at {api_url}")
            time.sleep(wait)
            release_json = get_release_json()

        if not release_json:
            raise RuntimeError("Timed out waiting for GitHub release creation!")
            
def delete_previous_draft_create_new_release(release, user, repo, token):
    headers = {'Authorization': 'token {}'.format(token)}
    api_url = 'https://api.github.com/repos/{user}/{repo}/releases'
    api_url = api_url.format(user=user, repo=repo)
    # List all Releases and extracting Release with draft status
    req = requests.get(api_url)
    for i in req.json():
        if i['draft'] == True and i['tag_name'] == release:
            draft_release_id = i['id']
            
    delete_api_url = api_url + '/ {release_id}'
    delete_req = requests.delete(delete_url,
                            headers=headers)
    delete_req.raise_for_status()


def github_release(release, user, repo, token):
    create_draft_release(release, user, repo, token)
    delete_previous_draft_create_new_release(release, user, repo, token)

        
def main():
    '''Main logic'''

    github_release(release, user, repo, token)
        
if __name__ == '__main__':
    main()
