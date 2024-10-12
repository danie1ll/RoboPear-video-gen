
import time
import requests

WORKFLOW = "67098f512977ecf2d8ca5959-v3"
KEY = "SG_87fdea15e4947255"

def run_flow(image_url: str, scene_prompt: str, video_prompt: str) -> dict:
    url = f"https://api.segmind.com/workflows/{WORKFLOW}"
    data = {
        "image": image_url,
        "scene_prompt": scene_prompt,
        "video_prompt": video_prompt
        # "str_bvcxq": "test",
    }

    headers = {
        'x-api-key': KEY,
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        raise Exception("Error running flow")


def poll_flow(url: str) -> dict:
    headers = {
        'x-api-key': KEY
    }
    interval_seconds = 2

    while True:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            body = response.json()
            if body['status'] == "PROCESSING":
                print(f"Flow is queued. Polling again in {interval_seconds} seconds...")
                time.sleep(interval_seconds)
                continue
            if body['status'] == "COMPLETED":
                return body['output']
            if body['status'] == "FAILED":
                raise Exception("Flow failed")
        else:
            raise


def main():
    image_url = "https://woodtrick.com/cdn/shop/files/00041000x1000.png"
    holiday = "Easter"
    season = "winter"

    scene_prompt = f"A product placed into a center of a composition on a wooden table. The product is surrounded by {holiday} items. Cozy and rustic {season} feeling. 4k. high resolution, 3d. Instagram ready."
    video_prompt = "light changes slightly"

    flow = run_flow(image_url, scene_prompt, video_prompt)
    if flow['status'] == "QUEUED":
        poll_result = poll_flow(flow['poll_url'])
        print(poll_result)
        
        # Check if poll_result is a string and attempt to parse it
        if isinstance(poll_result, str):
            import json
            try:
                poll_result = json.loads(poll_result)
            except json.JSONDecodeError:
                raise Exception("Failed to parse poll result as JSON")
        
        # Now handle the poll_result as a list of dictionaries
        if isinstance(poll_result, list) and len(poll_result) > 0:
            video_url = poll_result[0]['value']['data']
            print(f"Video generated: {video_url}")
    else:
        raise Exception("Flow not queued")



if __name__ == "__main__":
    main()