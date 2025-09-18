from itertools import batched
import re
from typing import cast
from uuid import UUID
import click

from cnschn_video.render import MetaAPI, fetch_video_info, fetch_video_list, set_video_meta


@click.group()
def cnschn_videos():
    pass


@cnschn_videos.command()
@click.option('-p', '--only-public', is_flag=True)
def list_videos(only_public: bool):
    videos = fetch_video_list(only_public)

    for video in videos:
        click.echo(video['title'], nl=False)
        click.secho(f' {video['guid']}', fg='green')


@cnschn_videos.command()
@click.argument('video_id', type=UUID)
def get_meta(video_id: UUID):
    video = fetch_video_info(video_id)

    click.echo('Current meta for video "', nl=False)
    click.secho(video['title'], fg='green', nl=False)
    click.echo('":',)
    meta_api = cast(MetaAPI, video['metaTags'])
    for meta in meta_api:
        click.secho('\n' + meta['property'] + ':', fg='green')
        click.echo(meta['value'])


@cnschn_videos.command()
@click.argument('video_id', type=UUID)
def edit_meta(video_id: UUID):
    video = fetch_video_info(video_id)
    meta_api = cast(MetaAPI, video['metaTags'])

    MARKER = '# Everything above is ignored.\n'

    input = f'# Editing tags for video "{ video["title"] }".\n'
    input += '# Tags begin with a "$" sign, their values start on the next line.\n'
    input += MARKER

    for meta in meta_api:
        input += f'\n${meta["property"]}\n'
        input += f'{meta["value"]}\n'

    output = click.edit(input)

    if output is None:
        click.echo('Cancelled.')
        return

    # Remove the help text above
    stripped = output.split(MARKER, 1)[1]

    # Split by tag pattern, skipping the first string before the first tag name
    split = re.split(r'^\$(\w+)$', stripped, flags=re.MULTILINE)[1:]

    new_meta_api: MetaAPI = []

    for chunk in batched(split, 2):
        new_meta_api.append({
            'property': chunk[0],
            'value': chunk[1].strip()
        })

    set_video_meta(video_id, new_meta_api)
    click.echo('Updated successfully')


if __name__ == '__main__':
    cnschn_videos()
