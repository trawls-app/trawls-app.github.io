import requests
import json
from github import Github


def get_browser_download_url(assets, ending):
    for a in assets:
        if a.name.endswith(ending):
            return a.browser_download_url

    raise ValueError("Could not find asset with ending '{}'.".format(ending))


def get_sig(assets, ending):
    for a in assets:
        if a.name.endswith(ending + ".sig"):
            resp = requests.get(a.browser_download_url)
            resp.raise_for_status()
            return resp.text

    raise ValueError("Could not find asset with ending '{}.sig'.".format(ending))


if __name__ == '__main__':
    repo = Github().get_repo("trawls-app/trawls")
    release = repo.get_latest_release()

    if release.draft:
        raise Exception("Release is still a draft")

    release_assets = release.get_assets()
    data = {
        "name": release.tag_name,
        "notes": release.body,
        "pub_date": release.published_at.isoformat(),
        "platforms": {
            "darwin": {
                "signature": get_sig(release_assets, ".app.tar.gz"),
                "url": get_browser_download_url(release_assets, ".app.tar.gz")
            },
            "linux": {
                "signature": get_sig(release_assets, ".AppImage.tar.gz"),
                "url": get_browser_download_url(release_assets, ".AppImage.tar.gz")
            },
            "win64": {
                "signature": get_sig(release_assets, ".msi.zip"),
                "url": get_browser_download_url(release_assets, ".msi.zip")
            }
        }
    }

    with open("../static_api/releases/current.json", "w") as fp:
        json.dump(data, fp)
