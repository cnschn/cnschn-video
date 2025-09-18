from datetime import timedelta
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from cnschn_video.config import bunny
from cnschn_video.render import fetch_video_info, fetch_video_list

app = FastAPI()


static_app = StaticFiles(directory='static')
app.mount('/static', static_app, name='static')

templates = Jinja2Templates(directory='templates')

def format_runtime(seconds: int) -> str:
    return str(timedelta(seconds=seconds)).removeprefix('0:')

templates.env.filters['format_runtime'] = format_runtime

@app.get('/', response_class=HTMLResponse)
def read_root(request: Request):
    videos = fetch_video_list()
    return templates.TemplateResponse(
        request=request, name='index.html', context={'videos': videos, 'bunny': bunny}
    )

@app.get('/watch/{video_id}/', response_class=HTMLResponse)
def read_video(request: Request, video_id: UUID):
    video = fetch_video_info(video_id)
    return templates.TemplateResponse(
        request=request, name='video.html', context={'video': video, 'bunny': bunny}
    )
