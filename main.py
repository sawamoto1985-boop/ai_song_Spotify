import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from supabase import create_client
import time

# --- 設定 ---
TABLE_NAME = "ai_song_spotify_ranking"
MIN_POPULARITY = 10
TARGET_COUNT = 500

# 認証
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
))
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

def calculate_ai_score(track, feat):
    score = 0
    full_text = (track['name'] + track['artists'][0]['name']).lower()
    # ツール名が含まれるか (+60)
    if any(k in full_text for k in ['suno', 'udio', 'aiva', 'soundraw']):
        score += 60
    # インスト度が高い (+20)
    if feat and feat['instrumentalness'] > 0.8:
        score += 20
    # 人気度基準クリア (+20)
    if track['popularity'] >= 10:
        score += 20
    return score

def collect_songs(query, market):
    print(f"🚀 {market} 市場の検索開始...")
    count = 0
    for offset in range(0, 1000, 50):
        if count >= TARGET_COUNT: break
        
        res = sp.search(q=query, limit=50, offset=offset, type='track', market=market)
        tracks = res['tracks']['items']
        if not tracks: break
        
        ids = [t['id'] for t in tracks]
        features = sp.audio_features(ids)
        
        for t, f in zip(tracks, features):
            if t['popularity'] < MIN_POPULARITY: continue
            
            score = calculate_ai_score(t, f)
            if score >= 60:
                data = {
                    "market": market,
                    "popularity": t['popularity'],
                    "ai_score": score,
                    "name": t['name'],
                    "artist": t['artists'][0]['name'],
                    "release_date": t['album']['release_date'],
                    "instrumentalness": f['instrumentalness'] if f else 0,
                    "url": t['external_urls']['spotify']
                }
                # 指定されたテーブル名へ保存
                supabase.table(TABLE_NAME).upsert(data, on_conflict="url").execute()
                count += 1
                if count >= TARGET_COUNT: break
        
        print(f"取得済み: {count}件...")
        time.sleep(0.1)

# 邦楽と洋楽の実行
collect_songs('"Suno" OR "Udio" (AI歌唱 OR 日本 OR JPOP)', 'JP')
collect_songs('"Suno" OR "Udio" -JPOP -日本', 'US')
