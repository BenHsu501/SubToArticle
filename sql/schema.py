import sqlite3

# 连接到 SQLite 数据库
# 如果数据库不存在，会自动创建一个数据库文件
conn = sqlite3.connect('output/yt_info.db')

# 创建一个 cursor 对象
c = conn.cursor()

# 创建表
c.execute('''
CREATE TABLE videos (
    id TEXT PRIMARY KEY,
    title TEXT,
    url TEXT,
    description TEXT,
    duration INTEGER,
    view_count INTEGER,
    webpage_url TEXT,
    webpage_url_domain TEXT,
    extractor TEXT,
    playlist_title TEXT,
    playlist_id TEXT,
    playlist_uploader TEXT,
    playlist_uploader_id TEXT,
    n_entries INTEGER,
    duration_string TEXT,
    upload_date TEXT,
    has_subtitles TEXT DEFAULT 'No',
    type_subtitle TEXT DEFAULT 'No',
    has_address_subtitles TEXT DEFAULT 'No',
    has_generated_article TEXT DEFAULT 'No',
    has_uploaded_article TEXT DEFAULT 'No'
);
''')

# 提交事务
conn.commit()

# 关闭连接
conn.close()
