import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from supabase import create_client
import time

# --- 設定 ---
TABLE_NAME = "ai_song_spotify_ranking"
MIN_POPULARITY = 10
TARGET_COUNT = 500

# 認証設定
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

# デバッグ用：IDの最初だけ表示（ログで確認用）
if client_id:
    print(f"🛰️ 接続テスト開始... ClientID末尾: {client_id[-4:]}")

try:
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    # 接続テスト（これを1回挟むことで403の原因を切り分けます）
    sp.search(q='test', limit=1)
    print("✅ Spotify API への接続に成功しました！")
except Exception as e:
    print(f"❌ 接続エラー: {e}")
    print("ヒント: Spotify Dashboardの 'Edit' で 'Web API' にチェックが入っているか確認してください。")

# Supabase接続
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
    print(f"🚀 {market} 市場の検索を開始します...")
    count = 0
    for offset in range(0, 1000, 50):
        if count >= TARGET_COUNT: break
        
        try:
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
                    supabase.table(TABLE_NAME).upsert(data, on_conflict="url").execute()
                    count += 1
                    if count >= TARGET_COUNT: break
            
            print(f"📊 {market}: {count}件 保存済み")
            time.sleep(0.1)
        except Exception as e:
            print(f"⚠️ ループ内でエラーが発生: {e}")
            break

# 実行
collect_songs('"Suno" OR "Udio" (AI歌唱 OR 日本 OR JPOP)', 'JP')
collect_songs('"Suno" OR "Udio" -JPOP -日本', 'US')
