import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from supabase import create_client
import time

# --- 設定 ---
TABLE_NAME = "ai_song_spotify_ranking"
MIN_POPULARITY = 10
TARGET_COUNT = 100 # 件数を少し戻しました

# 認証
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
))
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

def calculate_ai_score_simple(track):
    """オーディオ特性を使わず、名前と人気度だけでスコア計算"""
    score = 0
    full_text = (track['name'] + track['artists'][0]['name']).lower()
    # ツール名が含まれるか (+80)
    if any(k in full_text for k in ['suno', 'udio', 'aiva', 'soundraw']):
        score += 80
    # 人気度基準クリア (+20)
    if track['popularity'] >= 10:
        score += 20
    return score

def collect_songs(query, market):
    print(f"--- {market} 検索開始 ---")
    try:
        # 50件ずつ取得
        for offset in range(0, 500, 50):
            res = sp.search(q=query, limit=50, offset=offset, type='track', market=market)
            tracks = res['tracks']['items']
            if not tracks: break
            
            print(f"✅ {len(tracks)}件のデータを処理中...")
            
            for t in tracks:
                # 人気度10未満はスキップ
                if t['popularity'] < MIN_POPULARITY:
                    continue
                
                score = calculate_ai_score_simple(t)
                
                # スコアが一定以上のものだけ保存
                if score >= 80:
                    data = {
                        "market": market,
                        "popularity": t['popularity'],
                        "ai_score": score,
                        "name": t['name'],
                        "artist": t['artists'][0]['name'],
                        "release_date": t['album']['release_date'],
                        "url": t['external_urls']['spotify']
                        # instrumentalness は取得制限のため削除
                    }
                    # Supabaseへ保存
                    try:
                        supabase.table(TABLE_NAME).upsert(data, on_conflict="url").execute()
                    except Exception as e:
                        print(f"Supabase保存エラー: {e}")
            
            time.sleep(1) # サーバー負荷軽減
            
        print(f"--- {market} 完了 ---")
            
    except Exception as e:
        print(f"❌ エラー発生: {e}")

# 実行（JPとUS両方）
collect_songs('"Suno" OR "Udio" (AI歌唱 OR 日本 OR JPOP)', 'JP')
collect_songs('"Suno" OR "Udio" -JPOP -日本', 'US')
