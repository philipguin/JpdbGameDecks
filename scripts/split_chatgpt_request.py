import argparse
import os
import shutil
# import asyncio
# import aiohttp
# from tqdm.asyncio import tqdm
# from tenacity import retry, wait_fixed, stop_after_attempt
import requests
from tqdm import tqdm

def split_into_parts(text, max_char_count):
    parts = []
    current_part = []
    current_length = 0

    for paragraph in text.split('\n\n'):
        paragraph_length = len(paragraph) + 2  # Adding 2 for the double newlines
        if current_length + paragraph_length > max_char_count:
            parts.append('\n\n'.join(current_part))
            current_part = [paragraph]
            current_length = paragraph_length
        else:
            current_part.append(paragraph)
            current_length += paragraph_length

    if current_part:
        parts.append('\n\n'.join(current_part))

    return parts


#@retry(wait=wait_fixed(2), stop=stop_after_attempt(5))
def submit_to_chat_gpt(prompt, text, api_url, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "messages": [{"role": "user", "content": f"{prompt}\n\n```\n{text}\n```"}],
    }
    # async with session.post(api_url, json=data, headers=headers) as response:
    #     response.raise_for_status()
    #     return await response.text()

    response = requests.post(api_url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']


def main():
    parser = argparse.ArgumentParser(description="Split input file and submit parts to Chat-GPT 4o.")
    parser.add_argument('prompt_file', type=str, help='Path to the prompt file')
    parser.add_argument('input_file', type=str, help='Path to the input file')
    parser.add_argument('max_char_count', type=int, help='Maximum character count per part')
    parser.add_argument('output_folder', type=str, help='Folder to store output files')
    parser.add_argument('api_key', type=str, help='OpenAI API key')
    args = parser.parse_args()

    # Make directories
    if os.path.exists(args.output_folder):
        shutil.rmtree(args.output_folder)

    os.makedirs(args.output_folder, exist_ok=True)

    # Process inputs
    with open(args.prompt_file, 'r', encoding='utf-8') as pf:
        prompt = pf.read().strip()

    with open(args.input_file, 'r', encoding='utf-8') as inf:
        input_text = inf.read()

    parts = split_into_parts(input_text, args.max_char_count)

    # Submission to Chat-GPT

    api_url = "https://api.openai.com/v1/chat/completions"

    # async with aiohttp.ClientSession() as session:
    #     tasks = [
    #         submit_to_chat_gpt(prompt, part, session, api_url, args.api_key)
    #         for part in parts
    #     ]
    #     responses = []
    #     for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Submitting parts"):
    #         response = await task
    #         responses.append(response)

    for i, part in enumerate(tqdm(parts, desc="Submitting parts")):
        response = submit_to_chat_gpt(prompt, part, api_url, args.api_key)

        output_path = os.path.join(args.output_folder, f"part_{i}.txt")
        with open(output_path, 'w', encoding='utf-8') as outf:
            outf.write(response)

if __name__ == '__main__':
    #asyncio.run(main())
    main()
