import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from supabase import create_client
import time

# --- テスト用に大幅に絞り込み ---
TABLE_NAME = "ai_song_spotify_ranking"
MIN_POPULARITY = 10
TARGET_COUNT = 50 # 500件から50件に大幅削減

# 認証
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
))
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

def calculate_ai_score(track, feat):
    score = 0
    full_text = (track['name'] + track['artists'][0]['name']).lower()
    if any(k in full_text for k in ['suno', 'udio', 'aiva', 'soundraw']):
        score += 60
    if feat and feat['instrumentalness'] > 0.8:
        score += 20
    if track['popularity'] >= 10:
        score += 20
    return score

def collect_songs(query, market):
    print(f"--- {market} 検索開始 ---")
    try:
        # まず検索自体ができるかテスト
        res = sp.search(q=query, limit=10, type='track', market=market)
        tracks = res['tracks']['items']
        print(f"✅ 検索成功: {len(tracks)}件見つかりました")
        
        count = 0
        for i, t in enumerate(tracks):
            if count >= TARGET_COUNT: break
            
            # 人気度チェック
            if t['popularity'] < MIN_POPULARITY:
                continue
            
            # 1曲ずつオーディオ特性を取得（慎重に）
            try:
                f_list = sp.audio_features([t['id']])
                f = f_list[0] if f_list else None
                
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
                    supabase.table(TABLE_NAME).upsert(data, on_conflict="url").execute()
                    count += 1
                    print(f"[{count}] 保存完了: {t['name']}")
            except Exception as e:
                print(f"❌ 曲単位のエラー ({t['name']}): {e}")
            
            time.sleep(0.5) # 負荷をかけないよう待機時間を長く設定
            
    except Exception as e:
        print(f"❌ 検索中にエラーが発生: {e}")

# 実行
collect_songs('"Suno" OR "Udio" (AI歌唱 OR 日本 OR JPOP)', 'JP')
