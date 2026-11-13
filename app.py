import os
import re
import json
import time
import uuid
import random
import shutil
import logging
import tempfile
import threading
import subprocess
from datetime import datetime
from urllib.parse import urlparse

import requests
import yt_dlp
from bs4 import BeautifulSoup
from flask import Flask, Response, jsonify, render_template, request
from user_agent import generate_user_agent
from werkzeug.middleware.proxy_fix import ProxyFix

channel = "https://t.me/celestecutiee"
contact = "https://t.me/rriellqt"

logfile = "logs.json"
cooldown = 10
lifespan = 3600

cooldowns = {}
vault = {}
guard = threading.Lock()
slots = threading.BoundedSemaphore(3)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

formats = {
    "insta": ["video", "image", "slideshow"],
    "fb": ["video", "audio"],
    "tiktok": ["video", "audio", "montage"],
    "pin": ["video", "image"],
    "yt": ["video", "audio"],
    "reddit": ["video", "image", "audio"],
    "x": ["video", "image"],
    "vimeo": ["video", "audio"],
    "dailymotion": ["video"],
    "twitch": ["video", "audio"],
    "soundcloud": ["audio"],
    "tumblr": ["video", "image"],
    "9gag": ["video", "image"],
    "streamable": ["video"],
    "imgur": ["video", "image"],
    "bilibili": ["video"],
    "rumble": ["video"],
    "flickr": ["video", "image"],
    "bandcamp": ["audio"],
    "kick": ["video"],
    "threads": ["video", "image"],
    "linkedin": ["video"],
    "snapchat": ["video", "image"],
    "bluesky": ["video", "image"],
    "mastodon": ["video", "image"],
    "odysee": ["video"],
    "peertube": ["video"],
    "loom": ["video"],
    "vidio": ["video"],
    "vkvideo": ["video", "audio"],
    "audiomack": ["audio"],
    "audius": ["audio"],
    "mixcloud": ["audio"],
    "jamendo": ["audio"],
    "freesound": ["audio"],
    "giphy": ["image", "video"],
    "deviantart": ["image"],
    "photobucket": ["image"],
    "pixiv": ["image"],
    "newgrounds": ["video", "image", "audio"]
}

categories = {
    "social": ["insta", "fb", "tiktok", "x", "threads", "linkedin", "snapchat", "bluesky", "mastodon"],
    "video": ["yt", "twitch", "kick", "vimeo", "dailymotion", "rumble", "streamable", "bilibili", "odysee", "peertube", "loom", "vidio", "vkvideo"],
    "audio": ["soundcloud", "bandcamp", "audiomack", "audius", "mixcloud", "jamendo", "freesound"],
    "image": ["pin", "imgur", "flickr", "tumblr", "reddit", "9gag", "giphy", "deviantart", "photobucket", "pixiv", "newgrounds"]
}

names = {
    "insta": "ɪɴꜱᴛᴀɢʀᴀᴍ",
    "fb": "ꜰᴀᴄᴇʙᴏᴏᴋ",
    "tiktok": "ᴛɪᴋᴛᴏᴋ",
    "pin": "ᴘɪɴᴛᴇʀᴇꜱᴛ",
    "yt": "ʏᴏᴜᴛᴜʙᴇ",
    "reddit": "ʀᴇᴅᴅɪᴛ",
    "x": "x / ᴛᴡɪᴛᴛᴇʀ",
    "vimeo": "ᴠɪᴍᴇᴏ",
    "dailymotion": "ᴅᴀɪʟʏᴍᴏᴛɪᴏɴ",
    "twitch": "ᴛᴡɪᴛᴄʜ",
    "soundcloud": "ꜱᴏᴜɴᴅᴄʟᴏᴜᴅ",
    "tumblr": "ᴛᴜᴍʙʟʀ",
    "9gag": "9ɢᴀɢ",
    "streamable": "ꜱᴛʀᴇᴀᴍᴀʙʟᴇ",
    "imgur": "ɪᴍɢᴜʀ",
    "bilibili": "ʙɪʟɪʙɪʟɪ",
    "rumble": "ʀᴜᴍʙʟᴇ",
    "flickr": "ꜰʟɪᴄᴋʀ",
    "bandcamp": "ʙᴀɴᴅᴄᴀᴍᴘ",
    "kick": "ᴋɪᴄᴋ",
    "threads": "ᴛʜʀᴇᴀᴅꜱ",
    "linkedin": "ʟɪɴᴋᴇᴅɪɴ",
    "snapchat": "ꜱɴᴀᴘᴄʜᴀᴛ",
    "bluesky": "ʙʟᴜᴇꜱᴋʏ",
    "mastodon": "ᴍᴀꜱᴛᴏᴅᴏɴ",
    "odysee": "ᴏᴅʏꜱᴇᴇ",
    "peertube": "ᴘᴇᴇʀᴛᴜʙᴇ",
    "loom": "ʟᴏᴏᴍ",
    "vidio": "ᴠɪᴅɪᴏ",
    "vkvideo": "ᴠᴋ ᴠɪᴅᴇᴏ",
    "audiomack": "ᴀᴜᴅɪᴏᴍᴀᴄᴋ",
    "audius": "ᴀᴜᴅɪᴜꜱ",
    "mixcloud": "ᴍɪxᴄʟᴏᴜᴅ",
    "jamendo": "ᴊᴀᴍᴇɴᴅᴏ",
    "freesound": "ꜰʀᴇᴇꜱᴏᴜɴᴅ",
    "giphy": "ɢɪᴘʜʏ",
    "deviantart": "ᴅᴇᴠɪᴀɴᴛᴀʀᴛ",
    "photobucket": "ᴘʜᴏᴛᴏʙᴜᴄᴋᴇᴛ",
    "pixiv": "ᴘɪxɪᴠ",
    "newgrounds": "ɴᴇᴡɢʀᴏᴜɴᴅꜱ"
}

hosts = {
    "insta": ("instagram.com",),
    "fb": ("facebook.com", "fb.watch", "fb.com"),
    "tiktok": ("tiktok.com",),
    "pin": ("pinterest.com", "pin.it"),
    "yt": ("youtube.com", "youtu.be"),
    "reddit": ("reddit.com", "redd.it"),
    "x": ("x.com", "twitter.com"),
    "vimeo": ("vimeo.com",),
    "dailymotion": ("dailymotion.com", "dai.ly"),
    "twitch": ("twitch.tv",),
    "soundcloud": ("soundcloud.com",),
    "tumblr": ("tumblr.com",),
    "9gag": ("9gag.com",),
    "streamable": ("streamable.com",),
    "imgur": ("imgur.com",),
    "bilibili": ("bilibili.com", "b23.tv"),
    "rumble": ("rumble.com",),
    "flickr": ("flickr.com", "flic.kr"),
    "bandcamp": ("bandcamp.com",),
    "kick": ("kick.com",),
    "threads": ("threads.net", "threads.com"),
    "linkedin": ("linkedin.com",),
    "snapchat": ("snapchat.com",),
    "bluesky": ("bsky.app",),
    "mastodon": ("mastodon.social",),
    "odysee": ("odysee.com",),
    "peertube": ("peertube.tv",),
    "loom": ("loom.com",),
    "vidio": ("vidio.com",),
    "vkvideo": ("vk.com", "vkvideo.ru"),
    "audiomack": ("audiomack.com",),
    "audius": ("audius.co",),
    "mixcloud": ("mixcloud.com",),
    "jamendo": ("jamendo.com",),
    "freesound": ("freesound.org",),
    "giphy": ("giphy.com",),
    "deviantart": ("deviantart.com",),
    "photobucket": ("photobucket.com",),
    "pixiv": ("pixiv.net",),
    "newgrounds": ("newgrounds.com",)
}

def clock():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def readlogs():
    if os.path.exists(logfile):
        try:
            with open(logfile, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def savelogs(data):
    try:
        with open(logfile, "w") as f:
            json.dump(data[-100:], f, indent=4)
    except Exception:
        pass

def logaction(user_id, username, platform, fmt, status):
    with guard:
        logs = readlogs()
        logs.append({
            "time": clock(),
            "id": user_id,
            "user": username or "none",
            "platform": platform,
            "format": fmt,
            "status": status
        })
        savelogs(logs)

def fbdown(url, fmt):
    headers = {
        'User-Agent': generate_user_agent(),
        'Origin': 'https://fbdown.blog',
        'Referer': 'https://fbdown.blog/',
    }
    try:
        r = requests.post('https://fbdown.blog/get.php', headers=headers, data={'url': url}, timeout=15)
        raw = r.text.replace('\\/', '/')
        data = r.json()['data']
        hd = sd = "Not available"
        for m in data.get("medias", []):
            if m.get("quality") == "HD":
                hd = m["url"]
            elif m.get("quality") == "SD" and sd == "Not available":
                sd = m["url"]

        res = []
        if fmt == "video":
            if hd != "Not available":
                res.append({"quality": "HD", "url": hd})
            if sd != "Not available":
                res.append({"quality": "SD", "url": sd})

        if not res:
            return {"status": "error", "message": f"No {fmt} found."}
        return {"status": "success", "video": res}
    except Exception:
        return {"status": "error", "message": "Facebook extraction failed"}

def instadown(url, fmt):
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
            "extractor_args": {"instagram": {"player_client": ["android", "ios", "web"]}}
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats_list = []
        seen_urls = set()
        seen_qualities = set()

        if 'entries' in info:
            entries = info['entries']
        else:
            entries = [info]

        for entry in entries:
            if not entry: continue

            u = entry.get('url')
            ext = entry.get('ext', '')
            vcodec = entry.get('vcodec')
            acodec = entry.get('acodec')

            if u and u not in seen_urls:
                if fmt == 'video' and (vcodec != 'none' or ext in ('mp4', 'webm', 'mkv')):
                    q = "Original"
                    if q not in seen_qualities:
                        seen_urls.add(u)
                        seen_qualities.add(q)
                        formats_list.append({"quality": q, "url": u})
                elif fmt == 'audio' and (acodec != 'none' or ext in ('mp3', 'm4a', 'webm', 'aac', 'opus')):
                    q = "Audio"
                    if q not in seen_qualities:
                        seen_urls.add(u)
                        seen_qualities.add(q)
                        formats_list.append({"quality": q, "url": u})
                elif fmt == 'image' and ext in ('jpg', 'jpeg', 'png', 'webp'):
                    q = "Image"
                    if q not in seen_qualities:
                        seen_urls.add(u)
                        seen_qualities.add(q)
                        formats_list.append({"quality": q, "url": u})

            for f in entry.get('formats', []):
                direct_url = f.get('url')
                if not direct_url or direct_url in seen_urls:
                    continue

                f_vcodec = f.get('vcodec')
                f_acodec = f.get('acodec')
                f_ext = f.get('ext', '')
                height = f.get('height')

                if fmt == 'video':
                    if f_vcodec == 'none' and f_ext not in ('mp4', 'webm', 'mkv'):
                        continue
                    q = f"{height}p" if height else "DASH Video"
                elif fmt == 'audio':
                    if f_acodec == 'none' and f_ext not in ('mp3', 'm4a', 'webm', 'aac', 'opus'):
                        continue
                    q = "Audio"
                elif fmt == 'image':
                    if f_ext not in ('jpg', 'jpeg', 'png', 'webp'):
                        continue
                    q = "Image"
                else:
                    continue

                if q in seen_qualities:
                    continue

                seen_qualities.add(q)
                seen_urls.add(direct_url)
                formats_list.append({"quality": q, "url": direct_url})

        if not formats_list and info.get("url") and fmt == 'video':
            formats_list.append({"quality": "Original", "url": info["url"]})

        def get_height(item):
            q = item['quality']
            if q == "Original":
                return 9999
            if q.endswith('p') and q[:-1].isdigit():
                return int(q[:-1])
            return 0

        formats_list.sort(key=get_height, reverse=True)

        if not formats_list:
            return {"status": "error", "message": f"No {fmt} found."}

        return {"status": "success", "video": formats_list}
    except Exception as e:
        clean = re.sub(r'\x1b\[[0-9;]*m', '', str(e))
        return {"status": "error", "message": f"Instagram failed: {clean}"}

def pindown(url, fmt):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'origin': 'https://www.expertstool.com',
        'referer': 'https://www.expertstool.com/pinterest-video-download/',
        'user-agent': generate_user_agent(),
    }
    data = {'url': url}
    try:
        response = requests.post('https://www.expertstool.com/pinterest-video-download/', headers=headers, data=data, timeout=20)
        html = response.text
        if "API Not Work" in html or "Invalid" in html:
            return {"status": "error", "message": "Invalid Pinterest URL"}

        soup = BeautifulSoup(html, 'html.parser')

        if fmt == 'video':
            for btn in soup.find_all('a', class_=re.compile(r'btn.*primary')):
                href = btn.get('href', '')
                if href.startswith('https://v') and '.mp4' in href:
                    return {"status": "success", "video": [{"quality": "Video", "url": href}]}

        if fmt == 'image':
            for img in soup.find_all('a', href=re.compile(r'pinimg\.com.*originals')):
                return {"status": "success", "video": [{"quality": "Photo", "url": img['href']}]}

        return {"status": "error", "message": f"No {fmt} found."}
    except Exception:
        return {"status": "error", "message": "Pinterest extraction failed"}

def ytdown(url, fmt):
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
            "extractor_args": {"youtube": {"player_client": ["android", "ios"]}}
        }

        if fmt == 'audio':
            ydl_opts["format"] = "bestaudio/best"
        else:
            ydl_opts["format"] = "best[ext=mp4][vcodec!=none][acodec!=none]/best"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats_list = []
        seen_urls = set()

        for f in info.get("formats", []):
            direct_url = f.get("url")
            if not direct_url or direct_url in seen_urls:
                continue

            vcodec = f.get("vcodec")
            acodec = f.get("acodec")

            if vcodec == "none" and acodec == "none":
                continue

            if fmt == 'audio' and vcodec != "none":
                continue
            if fmt == 'video' and (vcodec == "none" or acodec == "none"):
                continue

            seen_urls.add(direct_url)
            q = "Audio" if vcodec == "none" else (f.get("format_note") or f.get("resolution") or "Original")
            formats_list.append({"quality": q, "url": direct_url})

        if not formats_list:
            return {"status": "error", "message": f"No {fmt} found."}

        return {"status": "success", "video": formats_list}
    except Exception as e:
        clean = re.sub(r'\x1b\[[0-9;]*m', '', str(e))
        return {"status": "error", "message": f"YouTube failed: {clean}"}

def maketiktokmontage(images, music_url):
    if not images:
        return {"status": "error", "message": "No photos found in this TikTok post."}
    if not music_url:
        return {"status": "error", "message": "TikTok did not provide the photo post's music track."}
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        return {"status": "error", "message": "FFmpeg and ffprobe are required to combine TikTok photos and music. Install them, then try again."}

    workdir = tempfile.mkdtemp(prefix="media_drift_")
    output_path = os.path.join(workdir, "tiktok_montage.mp4")

    try:
        image_paths = []
        headers = {"User-Agent": generate_user_agent()}

        for index, image_url in enumerate(images[:35]):
            response = requests.get(image_url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            image_path = os.path.join(workdir, f"image_{index:03d}.jpg")
            with open(image_path, "wb") as image_file:
                for chunk in response.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        image_file.write(chunk)
            if os.path.getsize(image_path) == 0:
                raise ValueError("A TikTok photo could not be downloaded.")
            image_paths.append(image_path)
            response.close()

        if not image_paths:
            raise ValueError("No downloadable photos were found in this post.")

        music_path = os.path.join(workdir, "soundtrack.mp3")
        response = requests.get(music_url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        with open(music_path, "wb") as music_file:
            for chunk in response.iter_content(chunk_size=1024 * 64):
                if chunk:
                    music_file.write(chunk)
        response.close()
        if os.path.getsize(music_path) == 0:
            raise ValueError("The TikTok soundtrack could not be downloaded.")

        probe = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", music_path
            ],
            capture_output=True,
            text=True,
            timeout=20
        )
        if probe.returncode != 0:
            raise RuntimeError("Could not read the soundtrack duration. Check that ffprobe is installed.")

        try:
            music_duration = float(probe.stdout.strip())
        except (TypeError, ValueError):
            raise RuntimeError("Could not determine the soundtrack duration.")

        if music_duration <= 0:
            raise RuntimeError("The downloaded soundtrack has no valid duration.")

        total_duration = max(music_duration, len(image_paths) * 3)
        seconds_per_image = total_duration / len(image_paths)
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
        for image_path in image_paths:
            command.extend(["-loop", "1", "-t", f"{seconds_per_image:.3f}", "-i", image_path])
        command.extend(["-i", music_path])

        filters = []
        video_labels = []
        for index in range(len(image_paths)):
            label = f"v{index}"
            filters.append(
                f"[{index}:v]scale=720:1280:force_original_aspect_ratio=decrease,"
                f"pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24,format=yuv420p[{label}]"
            )
            video_labels.append(f"[{label}]")

        filters.append(
            f"{''.join(video_labels)}concat=n={len(image_paths)}:v=1:a=0[vout]"
        )
        filters.append(f"[{len(image_paths)}:a]apad[aout]")
        command.extend([
            "-filter_complex", ";".join(filters),
            "-map", "[vout]", "-map", "[aout]",
            "-t", str(total_duration),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
            "-movflags", "+faststart", output_path
        ])

        result = subprocess.run(command, capture_output=True, text=True, timeout=180)
        if result.returncode != 0 or not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
            detail = (result.stderr or "FFmpeg could not create the montage.").strip()
            raise RuntimeError(detail[-500:])

        return {
            "status": "success",
            "video": [{"quality": "Montage MP4", "url": output_path, "local": True}]
        }
    except Exception as e:
        shutil.rmtree(workdir, ignore_errors=True)
        clean = re.sub(r'\x1b\[[0-9;]*m', '', str(e))
        return {"status": "error", "message": f"Could not create TikTok montage: {clean[:250]}"}

def tikdown(url, fmt):
    try:
        r = requests.post('https://www.tikwm.com/api/', data={'url': url, 'hd': 1}, timeout=15)
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 0:
            return {"status": "error", "message": "TikTok post not found or unavailable"}

        v_data = data.get("data", {})
        images = v_data.get("images") or []
        play_url = v_data.get("play")
        hd_url = v_data.get("hdplay")
        music_url = v_data.get("music")

        formats_list = []

        if fmt == 'montage':
            return maketiktokmontage(images, music_url)
        elif fmt == 'video':
            if hd_url:
                formats_list.append({"quality": "HD", "url": hd_url})
            if play_url and play_url != hd_url:
                formats_list.append({"quality": "SD", "url": play_url})
        elif fmt == 'audio':
            if music_url:
                formats_list.append({"quality": "Audio", "url": music_url})

        if not formats_list:
            return {"status": "error", "message": f"No {fmt} found."}

        return {"status": "success", "video": formats_list}
    except Exception as e:
        logging.warning(f"TikTok extraction failed: {e}")
        return {"status": "error", "message": "TikTok extraction failed. Check the link and try again."}

def general(url, fmt):
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
            "format": "best[ext=mp4]/best"
        }

        if fmt == 'audio':
            ydl_opts["format"] = "bestaudio/best"
        elif fmt == 'video':
            ydl_opts["format"] = "best[ext=mp4][vcodec!=none]/best"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats_list = []
        seen_urls = set()

        for f in info.get("formats", []):
            direct_url = f.get("url")
            if not direct_url or direct_url in seen_urls:
                continue

            vcodec = f.get("vcodec")
            acodec = f.get("acodec")
            ext = f.get("ext", '')

            if vcodec == "none" and acodec == "none":
                continue

            if fmt == 'audio' and vcodec != "none":
                continue
            if fmt == 'video' and vcodec == "none":
                continue
            if fmt == 'image' and ext not in ('jpg', 'jpeg', 'png', 'webp'):
                continue

            seen_urls.add(direct_url)
            q = "Audio" if vcodec == "none" else (f.get("format_note") or f.get("resolution") or "Original")
            formats_list.append({"quality": q, "url": direct_url})

        if not formats_list and info.get("url") and fmt == 'video':
            formats_list.append({"quality": "Original", "url": info["url"]})

        if not formats_list:
            return {"status": "error", "message": f"No {fmt} found."}

        return {"status": "success", "video": formats_list}
    except Exception as e:
        clean = re.sub(r'\x1b\[[0-9;]*m', '', str(e))
        return {"status": "error", "message": f"Extraction failed: {clean}"}

extractors = {
    "insta": instadown,
    "fb": fbdown,
    "tiktok": tikdown,
    "pin": pindown,
    "yt": ytdown
}

def discern(url):
    parts = urlparse(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return None
    host = parts.hostname.lower()
    for platform, domains in hosts.items():
        if any(host == domain or host.endswith("." + domain) for domain in domains):
            return platform
    return None

def throttle(ip):
    now = time.time()
    for key in [key for key, stamp in cooldowns.items() if now - stamp > cooldown]:
        cooldowns.pop(key, None)
    if ip in cooldowns:
        return int(cooldown - (now - cooldowns[ip])) + 1
    cooldowns[ip] = now
    return 0

def stash(path):
    token = uuid.uuid4().hex
    vault[token] = {"path": path, "time": time.time()}
    return token

def purge():
    now = time.time()
    for token in [token for token, entry in vault.items() if now - entry["time"] > lifespan]:
        entry = vault.pop(token, None)
        if entry:
            shutil.rmtree(os.path.dirname(entry["path"]), ignore_errors=True)

def harvest(platform, url, fmt):
    return extractors.get(platform, general)(url, fmt)

@app.get("/")
def foyer():
    return render_template("index.html", channel=channel, contact=contact)

@app.get("/api/sites")
def atlas():
    return jsonify(categories=categories, names=names, formats=formats)

@app.get("/api/detect")
def augur():
    platform = discern(request.args.get("url", "").strip())
    if not platform:
        return jsonify(status="error", message="Unsupported or invalid link."), 400
    return jsonify(status="success", platform=platform, name=names[platform], formats=formats[platform])

@app.post("/api/fetch")
def forage():
    purge()
    body = request.get_json(silent=True) or {}
    url = str(body.get("url", "")).strip()
    fmt = str(body.get("fmt", "")).strip().lower()
    ip = request.remote_addr or "unknown"
    platform = discern(url)
    if not platform:
        return jsonify(status="error", message="Unsupported or invalid link."), 400
    if fmt not in formats[platform]:
        return jsonify(status="error", message=f"{fmt.capitalize()} is not available for this site."), 400
    wait = throttle(ip)
    if wait:
        return jsonify(status="error", message=f"Wait {wait}s before the next request.", wait=wait), 429
    with slots:
        started = time.time()
        data = harvest(platform, url, fmt)
        elapsed = time.time() - started
    if data.get("status") == "error":
        logaction(ip, "", platform, fmt, "failed")
        return jsonify(status="error", message=data.get("message", "Extraction failed.")), 502
    items = []
    for item in data.get("video", []):
        link = item.get("url")
        if not link or link == "Not available":
            continue
        local = bool(item.get("local"))
        if local:
            link = "/api/file/" + stash(link)
        items.append({"quality": item.get("quality", "Link"), "url": link, "local": local})
    if not items:
        logaction(ip, "", platform, fmt, "failed")
        return jsonify(status="error", message="No media found."), 404
    logaction(ip, "", platform, fmt, "success")
    return jsonify(status="success", platform=platform, name=names[platform], fmt=fmt, speed=round(elapsed, 2), items=items)

@app.get("/api/file/<token>")
def relay(token):
    entry = vault.pop(token, None)
    if not entry or time.time() - entry["time"] > lifespan or not os.path.isfile(entry["path"]):
        return jsonify(status="error", message="This file has expired. Fetch the link again."), 404
    path = entry["path"]
    size = os.path.getsize(path)

    def trickle():
        try:
            with open(path, "rb") as handle:
                while chunk := handle.read(65536):
                    yield chunk
        finally:
            shutil.rmtree(os.path.dirname(path), ignore_errors=True)

    return Response(trickle(), mimetype="video/mp4", headers={
        "Content-Disposition": f'attachment; filename="@rriellqt_{random.randint(100000, 999999)}.mp4"',
        "Content-Length": str(size)
    })

def broachserver():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)

if __name__ == "__main__":
    broachserver()