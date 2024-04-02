import time

from string import Template

import httpx
import pyperclip

from pynput import keyboard
from pynput.keyboard import Controller, Key

controller = Controller()

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_CONFIG = {
    "model": "mistral:7b-instruct-v0.2-q5_K_M",
    "keep_alive": "5m",
    "stream": False,
}

PROMPT_TEMPLATE = Template(
    """Your task is to take the text provided and rewrite it into a clear,
    grammatically correct version while preserving the original meaning as closely as possible.
    Correct any spelling mistakes, punctuation errors, verb tense issues, word choice problems,
    and other grammatical mistakes, preserve all new line characters:

$text

Return only the corrected text, don't include a preamble.
"""
)

PROMPT_TEMPLATE_FOR_OFFICIAL_MESSAGE = Template(
    """Your task is to take the text provided and rewrite the below message to be more official, polite and friendly.,
    The output must be clear,
    grammatically correct version while preserving the original meaning as closely as possible.
    Correct any spelling mistakes, punctuation errors, verb tense issues, word choice problems,
    and other grammatical mistakes, preserve all new line characters.
    Avoid using word kindly:

$text

Return only the corrected text, don't include a preamble.
"""
)


def fix_text(text):
    prompt = PROMPT_TEMPLATE.substitute(text=text)
    response = httpx.post(
        OLLAMA_ENDPOINT,
        json={"prompt": prompt, **OLLAMA_CONFIG},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if response.status_code != 200:
        print("Error", response.status_code)
        return None
    return response.json()["response"].strip()


def rewrite_official_text(text):
    prompt = PROMPT_TEMPLATE_FOR_OFFICIAL_MESSAGE.substitute(text=text)
    response = httpx.post(
        OLLAMA_ENDPOINT,
        json={"prompt": prompt, **OLLAMA_CONFIG},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if response.status_code != 200:
        print("Error", response.status_code)
        return None
    return response.json()["response"].strip()


def rewrite_selection():
    # 1. Copy selection to clipboard
    with controller.pressed(Key.cmd):
        controller.tap("c")

    # 2. Get the clipboard string
    time.sleep(0.1)
    text = pyperclip.paste()

    # 3. Fix string
    if not text:
        return
    fixed_text = rewrite_official_text(text)
    if not fixed_text:
        return

    # 4. Paste the fixed string to the clipboard
    pyperclip.copy(fixed_text)
    time.sleep(0.1)

    # 5. Paste the clipboard and replace the selected text
    with controller.pressed(Key.cmd):
        controller.tap("v")


def fix_typos():
    # 1. Copy selection to clipboard
    with controller.pressed(Key.cmd):
        controller.tap("c")

    # 2. Get the clipboard string
    time.sleep(0.1)
    text = pyperclip.paste()

    # 3. Fix string
    if not text:
        return
    fixed_text = fix_text(text)
    if not fixed_text:
        return

    # 4. Paste the fixed string to the clipboard
    pyperclip.copy(fixed_text)
    time.sleep(0.1)

    # 5. Paste the clipboard and replace the selected text
    with controller.pressed(Key.cmd):
        controller.tap("v")


def on_f9():
    fix_typos()


def on_f10():
    rewrite_selection()


with keyboard.GlobalHotKeys({"<101>": on_f9, "<109>": on_f10}) as h:
    h.join()
