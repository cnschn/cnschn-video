import mistune
import requests
from typing import Literal, cast
from uuid import UUID

from cnschn_video.config import bunny


MetaAPI = list[dict[Literal['property'] | Literal['value'], str]]
Meta = dict[str, str]

Video = dict[str, str | list[str] | MetaAPI]
VideoList = list[Video]


def preprocess_meta(video: Video) -> None:
    for meta in video.get('metaTags', []):
        match meta['property']:
            case 'description':
                description = meta['value'].strip()
                video['description'] = mistune.html(description)

                pars = description.split('\n\n')
                if len(pars) > 2:
                    description_short = '\n\n'.join(pars[:2] + ['...'])
                else:
                    description_short = description

                video['descriptionShort'] = mistune.html(description_short)
            case 'tags':
                video['tags'] = meta['value'].split('\n')
            case _:
                print(f'Unknown meta tag "{meta["property"]}"')


def fetch_video_info(guid: UUID) -> Video:
    url = f'https://video.bunnycdn.com/library/{ bunny.library_id }/videos/{ guid }'
    res = requests.get(url, headers={'AccessKey': bunny.api_key})

    video: Video = res.json()
    preprocess_meta(video)

    return video


def fetch_video_meta(guid: UUID) -> MetaAPI:
    video: Video = fetch_video_info(guid)

    meta = video['metaTags']
    return cast(MetaAPI, meta)


def set_video_meta(guid: UUID, meta: MetaAPI):
    url = f'https://video.bunnycdn.com/library/{ bunny.library_id }/videos/{ guid }'
    res = requests.post(
        url,
        headers={'AccessKey': bunny.api_key},
        json={'metaTags': meta}
    )
    res.raise_for_status()


def fetch_video_list(only_public: bool=True) -> VideoList:
    url = f'https://video.bunnycdn.com/library/{ bunny.library_id }/videos'
    if only_public:
        url += f'?collection={ bunny.public_collection_id }'

    res = requests.get(url, headers={'AccessKey': bunny.api_key})
    videos: VideoList = res.json()['items']

    for video in videos:
        preprocess_meta(video)

    return videos

