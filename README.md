# Automated-Blog-Post-Creation-Framework
[中文閱讀](docs/README_ZH.md)
## Introduction
Do you often bookmark countless video links only to never open them again? Are these videos too lengthy, making it difficult to find time to watch? These deterrents can cause you to miss out on crucial information. In this project, you can batch download subtitles from specific YouTubers and generate articles from them, allowing you to quickly absorb information. This way, you can stay informed without spending hours watching videos.

* This article was generated by another GitHub project that can utilize copywriting models, such as 'AIDA: Attention-Interest-Desire-Action'.
## Features: Highlight the key features and benefits of the project.

## Setup
Download docker image from docker hub or gitth conle this repository.

    docker pull benjiminhsu/automated-blog-post-creation-framework

Run the docker image and export openai key.

    docker run -it -e OPENAI_API_KEY={OPENAI_API_KEY} benjiminhsu/automated-blog-post-creation-framework bash

Initial database 

    python3 sql/schmema.py
    python3 sql/data.py
    


## Usage: Explain how to use the project with examples.


## Project Detail
This project uses the Python package yt-dlp to retrieve information about YouTubers, storing the data in sqlite and then using an OpenAI model to generate articles.

The articles are based on video subtitles, which may be automatically generated and thus may not always be accurate. Users should be aware of this.