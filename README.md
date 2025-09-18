# cnschn-video

Tooling to statically generate my videos page.

Videos are hosted on bunny.net, the scripts in this repo use the bunny.net API to fetch all the
information needed to generate the pages.


## Running

Needs environment variable with bunny credentials, see `.env-example`. Then

```
> ./preprocess.sh && uv run --env-file .env build.py
```
