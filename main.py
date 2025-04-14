import time

from os import environ
from string import Template

import ollama
import pyperclip

from pynput import keyboard
from pynput.keyboard import Controller, Key

environ["NO_PROXY"] = "localhost"
environ["HTTP_PROXY"] = ""
environ["HTTPS_PROXY"] = ""

CLIENT = ollama.Client(host="http://localhost:11434", timeout=180)
# MODEL = "phi4:14b-q8_0"
# MODEL = "mistral-small:24b-instruct-2501-q8_0"
MODEL = "mistral-small3.1:24b-instruct-2503-q8_0"
CONTROLLER = Controller()

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
    """
    You are a professional communication editor specializing in formal business correspondence.
    Your task is to transform the provided text into a more professional, polite, and approachable message.

    Instructions:
    1. Rewrite the text to be more official while maintaining a warm, friendly tone
    2. Ensure perfect grammar, spelling, and punctuation
    3. Improve word choice and sentence structure for clarity and professionalism
    4. Preserve the original meaning and intent completely
    5. Maintain all paragraph breaks and formatting structure
    6. Avoid using the word "kindly" - use more varied professional alternatives
    7. Ensure proper verb tense consistency throughout
    8. Optimize for readability and conciseness

    Input:
    $text

    Output only the refined text without explanations, comments, or introductory statements.
    """
)


def fix_text(text):
    prompt = PROMPT_TEMPLATE.substitute(text=text)
    response = CLIENT.chat(model=MODEL, messages=[{"role": "user", "content": prompt}], keep_alive=3600)
    _return_value: str = response["message"]["content"].strip()
    return _return_value.removeprefix('"').removesuffix('"')


def rewrite_official_text(text):
    prompt = PROMPT_TEMPLATE_FOR_OFFICIAL_MESSAGE.substitute(text=text)
    response = CLIENT.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    _return_value: str = response["message"]["content"].strip()
    return _return_value.removeprefix('"').removesuffix('"')


def rewrite_selection():
    # 1. Copy selection to clipboard
    with CONTROLLER.pressed(Key.cmd):
        CONTROLLER.tap("c")

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
    with CONTROLLER.pressed(Key.cmd):
        CONTROLLER.tap("v")


def fix_typos():
    # 1. Copy selection to clipboard
    with CONTROLLER.pressed(Key.cmd):
        CONTROLLER.tap("c")

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
    with CONTROLLER.pressed(Key.cmd):
        CONTROLLER.tap("v")


def on_f9():
    fix_typos()


def on_f10():
    rewrite_selection()


with keyboard.GlobalHotKeys({"<101>": on_f9, "<109>": on_f10}) as h:
    h.join()
