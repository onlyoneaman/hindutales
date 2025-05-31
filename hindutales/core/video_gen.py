import os
import time
import requests
import base64
from typing import List, Optional
from dataclasses import dataclass
from hindutales.types.main import VideoGenInput

API_URL_VIDEO_GEN: str = "https://api.minimaxi.chat/v1/video_generation"
API_URL_VIDEO_STATUS: str = "https://api.minimaxi.chat/v1/query/video_generation"
API_URL_FILE_RETRIEVE: str = "https://api.minimaxi.chat/v1/files/retrieve"
S2V_MODEL: str = "S2V-01"
T2V_MODEL: str = "T2V-01"
POLL_INTERVAL_SECONDS: int = 10

@dataclass(frozen=True)
class VideoGenConfig:
    prompt: str
    image_path: Optional[str]
    output_path: str

class VideoGen:
    @staticmethod
    def _headers(api_key: str) -> dict:
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    @staticmethod
    def _invoke_video_generation(config: VideoGenInput) -> str:
        print("[VideoGen] Submitting video generation task...")
        payload = {
            "prompt": config.video_prompt,
            "model": S2V_MODEL
        }
        if config.image_path:
            with open(config.image_path, "rb") as f:
                image = f.read()
            image_b64 = base64.b64encode(image).decode("utf-8")
            payload["first_frame_image"] = image_b64
        response = requests.post(
            API_URL_VIDEO_GEN,
            headers=VideoGen._headers(config.api_key),
            json=payload
        )
        if response.status_code != 200:
            raise RuntimeError(f"Failed to submit video generation task: {response.text}")
        data = response.json()
        if "task_id" not in data:
            raise RuntimeError("No task_id returned from API.")
        print(f"[VideoGen] Task submitted successfully. Task ID: {data['task_id']}")
        return data["task_id"]

    @staticmethod
    def _query_video_generation(config: VideoGenConfig, task_id: str) -> Optional[str]:
        params = {"task_id": task_id}
        response = requests.get(
            API_URL_VIDEO_STATUS,
            headers=VideoGen._headers(config.api_key),
            params=params
        )
        if response.status_code != 200:
            raise RuntimeError(f"Failed to query video status: {response.text}")
        data = response.json()
        status = data.get("status", "Unknown")
        print(f"[VideoGen] Task status: {status}")
        if status == "Success":
            file_id = data.get("file_id")
            if not file_id:
                raise RuntimeError("No file_id found in successful response.")
            return file_id
        elif status in {"Preparing", "Queueing", "Processing"}:
            return None
        elif status == "Fail":
            raise RuntimeError("Video generation failed.")
        else:
            raise RuntimeError(f"Unknown status: {status}")

    @staticmethod
    def _fetch_video_result(config: VideoGenConfig, file_id: str) -> None:
        print("[VideoGen] Downloading generated video...")
        url = f"{API_URL_FILE_RETRIEVE}?file_id={file_id}"
        response = requests.get(url, headers=VideoGen._headers(config.api_key))
        if response.status_code != 200:
            raise RuntimeError(f"Failed to retrieve video file: {response.text}")
        data = response.json()
        download_url = data.get("file", {}).get("download_url")
        if not download_url:
            raise RuntimeError("No download_url found in file response.")
        video_data = requests.get(download_url).content
        with open(config.output_path, "wb") as f:
            f.write(video_data)
        print(f"[VideoGen] Video downloaded to: {os.path.abspath(config.output_path)}")

    @staticmethod
    def create_video(config: VideoGenConfig) -> None:
        VideoGen._validate_config(config)
        task_id = VideoGen._invoke_video_generation(config)
        print("[VideoGen] Waiting for video generation to complete...")
        while True:
            time.sleep(POLL_INTERVAL_SECONDS)
            try:
                file_id = VideoGen._query_video_generation(config, task_id)
                if file_id:
                    VideoGen._fetch_video_result(config, file_id)
                    print("[VideoGen] Video generation successful.")
                    break
            except RuntimeError as err:
                print(f"[VideoGen] Error: {err}")
                break
            video_url = get_video(video_input.task_id)
            if video_url:
                return video_url