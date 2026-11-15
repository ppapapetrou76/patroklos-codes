# pat-papapetrou

My personal site at https://patroklos.codes. It is one page built with [Hugo](https://gohugo.io)
from the data files in `data/`, and Cloudflare builds and publishes it on every push to `main`.

## Run it locally

Install Hugo, then:

```bash
hugo server
```

The site is at http://localhost:1313 and reloads when you save a file.

## Where things are

| What | File |
|---|---|
| Hero, numbers, README block, contact | `data/profile.yaml` |
| Talks and workshops | `data/talks.yaml` |
| Argo CD highlights and my projects | `data/opensource.yaml` |
| Conference history | `data/conferences.yaml` |
| Main Branch podcast | `data/podcast.yaml` |
| Books and articles | `data/writing.yaml` |
| SoftConf and the products | `data/founder.yaml` |
| Interviews | `data/interviews.yaml` |
| Page layout | `layouts/home.html` |
| Styles and script | `static/css/site.css`, `static/js/site.js` |

Each data file starts with a `section` block. That is the node in the resource tree: its label,
title, the one-line summary and the status on the right. Set `open: true` to have a node open when
the page loads.

## Add a talk

Add an entry at the top of `items` in `data/talks.yaml`:

```yaml
  - year: 2027
    title: "The title of the talk"
    event: "Conference, City"
    tags: [argo-cd, gitops]
    link_label: "Watch the recording"
    link: "https://..."
```

Articles, interviews, books and projects work the same way in their own files.

## What updates by itself

The `Update data` workflow runs once a day and runs `scripts/update_data.py`, which writes two files:

- `data/auto/episodes.json` has the Main Branch episodes from the YouTube channel feed. A new
  episode shows up with its title and link. To give it a description, add its video id under
  `episodes` in `data/podcast.yaml`.
- `data/auto/argocd_prs.json` has my latest merged Argo CD pull requests. They are listed under
  the highlights, and the highlights themselves stay hand-picked in `data/opensource.yaml`.

If a source cannot be reached the old file is kept. When something changed, the workflow commits
it, and Cloudflare rebuilds the site because of the push.

## Hosting

The site is a Cloudflare Workers project connected to this repository. `wrangler.jsonc` tells it to serve the `public` folder. The build settings are:

| Setting | Value |
|---|---|
| Build command | `hugo build --gc --minify` |
| Deploy command | `npx wrangler deploy` |
| Environment variable | `HUGO_VERSION` = `0.170.0` |

The daily update needs to commit, so in Settings, Actions, General, workflows are allowed to read
and write.
