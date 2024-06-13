import sqlite3

try:
    # 连接到 SQLite 数据库
    conn = sqlite3.connect('output/yt_info.db')
    print("数据库连接成功，版本为", sqlite3.version)

    # 创建一个 cursor 对象
    c = conn.cursor()

    # 确认数据表存在
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    print("数据库中的表：", tables)

    # 尝试插入数据
    video = ("test_video_id", "Test Video", "http://youtube.com/test", "Test description", 100, 150, "http://youtube.com/test", "youtube.com", "youtube", "Test Playlist", "TPL", "Test Uploader", "TU1", 1, "10:00", "20220101", "No", "No", "No")
    c.execute('''
    INSERT OR REPLACE INTO videos (id, title, url, description, duration, view_count, webpage_url, webpage_url_domain, extractor, playlist_title, playlist_id, playlist_uploader, playlist_uploader_id, n_entries, duration_string, upload_date, has_subtitles, has_generated_article, has_uploaded_article)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', video)

    # 提交事务
    conn.commit()
    print("数据插入并提交成功")

    # 查询数据
    c.execute("SELECT * FROM videos WHERE id = 'test_video_id';")
    results = c.fetchall()
    print("查询到的数据：", results)

except sqlite3.Error as error:
    print("数据库错误：", error)

finally:
    if conn:
        conn.close()
        print("数据库连接已关闭")
