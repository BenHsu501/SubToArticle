# SubToArticle
[中文閱讀](docs/README_ZH.md)
## How to use it in two steps？
### Step 1: Copy the youtube video ID you are interested in.
![**Alt text**](docs/image/get_video_id.png)
### Step 2: Get your article via script
![**All text**](docs/image/run_script.gif)

## Introduction
Do you often bookmark countless video links only to never open them again? Are these videos too lengthy, making it difficult to find time to watch? These deterrents can cause you to miss out on crucial information. In this project, you can batch download subtitles from specific YouTubers and generate articles from them, allowing you to quickly absorb information. This way, you can stay informed without spending hours watching videos.
## Features

- Fetch video IDs from YouTube playlists
- Download subtitles from YouTube videos
- Generate articles from video subtitles using OpenAI's API
- Flexible operation modes for full process or individual steps


## Prerequisites

- Python 3.7 or higher
- Required Python packages: `openai`, `yt-dlp`, `CopyCraftAPI`

## Installation
### Local install
1. Pull a docker image from docker hub:

   ```bash
    docker pull benjiminhsu/subtoarticle:1.0.6
   ```

2. Run a docker image as a container
    ```sh
    docker run -it --env OPENAI_API_KEY=<your_api_key> subtoarticle:1.0.6 bash

    ```

## Usage

### Command-Line Interface