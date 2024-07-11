# SubToArticle
[Read this in English](/README.md)

## SubToArticle 可以做什麼?
SubToArticle 是一個將字幕轉換成文章的工具。它可以讓你輕鬆地將 YouTube 影片字幕轉化為結構良好的文章，只需簡單的幾個步驟。

## 如何使用它完？
### 步驟 1: 複製你感興趣的 YouTube 視頻 ID。
<img src="../docs/image/get_video_id.png" alt="**Alt text**" width="400"/>

### 步驟 2: 使用腳本生成文章。
<img src="../docs/image/run_script.gif" alt="**All text**" width="400"/>

### 步驟 3: 查看生成的文章。
<img src="../docs/image/check_article.gif" alt="**All text**" width="400"/>

## 特點
- 從 YouTube 播放列表中獲取視頻 ID
- 下載 YouTube 視頻的字幕或使用 `Whisper` 轉錄音頻
- 使用 `ChatGPT` 從視頻字幕生成文章
- 靈活的操作模式，可執行整個流程或單獨的步驟

## 設置
### 先決條件

- Python 3.7 或更高版本
- 必需的 Python 套件：
  - `openai`
  - `yt-dlp`
  - `CopyCraftAPI` (從 GitHub 安裝)
- `ffmpeg`
- `sqlite3`
### 安裝
1. 從 Docker Hub pull Docker image：
    ```bash
    docker pull benjiminhsu/subtoarticle:1.0.6
    ```
2. 執行 Docker image :
    ```
    docker run -it --env OPENAI_API_KEY=<your_api_key> subtoarticle:1.0.6 bash
    ```


## 使用說明

* 生成單一影片文章
```sh
python main.py --video_id <VIDEO_ID>
```

* --subtitle_source 生成文章的字幕來源 
    * mp3(default): 字幕基於 mp3 檔案並透過 Whisper 生成，內容較穩定
    * subtitle: 影片自帶字幕，可能是人員上傳或系統`自動生成`，不一定每部影片都有，且自動生成字幕品質不一，適合大量生成
    * both: 優先使用 subtitle 模式，無字幕則用 mp3 模式
    ```sh
    python main.py --video_id <VIDEO_ID> --subtitle_source subtitle
    ```

* --mode main.py 執行的主要模式
    * full_process(default): 執行提取影片資訊、下載字幕、生成文章
    * fetch_video_id: 抓取 video id，批次下載資訊時使用
    ```sh
    python main.py --download_mode playlist --channel_url @BenHsu501
    ```
    * download_subtitle: 下載字幕使用，如果用於 `--download_mode playlist` 建議 `--subtitle_source subtitle`，否則whisper 辨識時間可能過長
    ```sh
    python main.py --download_mode playlist `--subtitle_source subtitle --channel_url @BenHsu501
    ```
    * generate_article: 生成文章
    ```sh
    python main.py --download_mode video_id --video_id <VIDEO_ID> --model gpt-4o
    ```
