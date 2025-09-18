from glob import glob
import os

from fastapi import HTTPException, Request
from fastapi.datastructures import URL
from fastapi.testclient import TestClient
from jinja2 import pass_context

from cnschn_video.render import fetch_video_list
from main import app, templates

def main():
    # custom url resolver to get "hashified" static files
    @pass_context
    def url_for( context, name, /, **path_params, ) -> URL:
        request: Request = context["request"]
        if name == 'static':
            # Instead of just looking up `path`, search for a glob including a checksum in the name
            path: str = path_params['path'].removeprefix('/')
            fname, _, ext = path.rpartition('.')
            if not fname:
                raise HTTPException(status_code=404)

            if ext == 'css':
                if path_globs := glob(f'{ fname }.*.{ ext }', root_dir='public/static/'):
                    # We just take the first result, shouldn't be multiple
                    path_params['path'] = path_globs[0]
                else:
                    raise HTTPException(status_code=404)
        return request.url_for(name, **path_params)

    templates.env.globals['url_for'] = url_for

    # Use a testclient to prerender all the pages
    client = TestClient(app, base_url=os.environ['VIDEOS_BASE_URL'])

    # Render index page (only gives public pages)
    print('Rendering index page...')
    resp = client.get('/')
    with open('public/index.html', 'wb') as f:
        f.write(resp.content)

    # Get all existing videos (non-public as well):
    print('Fetching list of videos...')
    videos = fetch_video_list(only_public=False)

    # Render pages
    os.mkdir('public/watch')
    for video in videos:
        print(f'Rendering video { video["guid"] }...')
        resp = client.get(f'/watch/{ video["guid"] }/')

        dir_name = f'public/watch/{ video["guid"] }'
        os.mkdir(dir_name)

        with open(f'{ dir_name }/index.html', 'wb') as f:
            f.write(resp.content)

if __name__ == '__main__':
    main()
