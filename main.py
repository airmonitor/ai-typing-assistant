import time

from string import Template

import ollama
import pyperclip

from pynput import keyboard
from pynput.keyboard import Controller, Key

CLIENT = ollama.Client(host="http://localhost:11434", timeout=60)
MODEL = "llama3:8b-instruct-q6_K"
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
