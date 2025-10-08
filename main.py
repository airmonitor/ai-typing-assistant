import time

from datetime import datetime, timedelta
from os import environ
from string import Template

import lmstudio as lms
import pyperclip

from pynput import keyboard
from pynput.keyboard import Controller, Key


def today():
    return datetime.today().strftime("%Y-%m-%d")


def yesterday():
    return (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")


environ["NO_PROXY"] = "localhost"
environ["HTTP_PROXY"] = ""
environ["HTTPS_PROXY"] = ""

MODEL_NAME = "mistralai/mistral-small-3.2"


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
MISTRAL_DEFAULT_SYSTEM_PROMPT = f"""
You are mistral-small, a Large Language Model (LLM) created by Mistral AI, a French startup headquartered in Paris.
You power an AI assistant called Le Chat.
Your knowledge base was last updated on 2023-10-01.
The current date is {today()}.

When you're not sure about some information or when the user's request requires up-to-date or specific data,
you must use the available tools to fetch the information. Do not hesitate to use tools whenever they can provide a
more accurate or complete response. If no relevant tools are available, then clearly state that you don't have the
information and avoid making up anything.
If the user's question is not clear, ambiguous, or does not provide enough context for you to
accurately answer the question, you do not try to answer it right away and you rather ask the user to
clarify their request (e.g. "What are some good restaurants around me?" => "Where are you?" or
"When is the next flight to Tokyo" => "Where do you travel from?").
You are always very attentive to dates, in particular you try to resolve dates (e.g. "yesterday" is {yesterday()}) and
when asked about information at specific dates, you discard information that is at another date.
You follow these instructions in all languages, and always respond to the user in the language they use or request.
Next sections describe the capabilities that you have.

# WEB BROWSING INSTRUCTIONS

You cannot perform any web search or access internet to open URLs, links etc.
If it seems like the user is expecting you to do so, you clarify the situation and ask the user
to copy paste the text directly in the chat.

# MULTI-MODAL INSTRUCTIONS

You have the ability to read images, but you cannot generate images. You also cannot transcribe audio files or videos.
You cannot read nor transcribe audio files or videos.

# TOOL CALLING INSTRUCTIONS

You may have access to tools that you can use to fetch information or perform actions.
You must use these tools in the following situations:

1. When the request requires up-to-date information.
2. When the request requires specific data that you do not have in your knowledge base.
3. When the request involves actions that you cannot perform without tools.

Always prioritize using tools to provide the most accurate and helpful response.
If tools are not available, inform the user that you cannot perform the requested action at the moment.

Return output in the original language in which that message was written.

"""

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
    """
    Correct the provided text

    """
    prompt = PROMPT_TEMPLATE.substitute(text=text)
    model = lms.llm(MODEL_NAME)
    response = model.respond(prompt)
    return response.content.removeprefix('"').removesuffix('"')


def rewrite_official_text(text):
    """
    Parameters:
        text (str): The input text to be rewritten in a more official and professional manner

    Functionality:
        This function takes an input text string, formats it according to a predefined template for official messages,
        and processes it through an LLM model to generate a more professional,
        polite, and grammatically correct version.
        The function uses a specific system prompt to guide the model's behavior and applies a low temperature setting
        for more deterministic output.

    Arguments:
        text: The input string to be rewritten

    Returns:
        str: The processed text with improved professionalism and correctness, without surrounding quotation marks
    """
    prompt = PROMPT_TEMPLATE_FOR_OFFICIAL_MESSAGE.substitute(text=text)
    lms.Chat(initial_prompt=MISTRAL_DEFAULT_SYSTEM_PROMPT)
    model = lms.llm(MODEL_NAME)
    response = model.respond(prompt, config={"temperature": 0.15})
    return response.content.removeprefix('"').removesuffix('"')


def rewrite_selection():
    """
    Parameters:
        None: This function operates on the current text selection in the active application

    Functionality:
        This function performs a sequence of operations to rewrite selected text in
        a more official and professional manner.
        It copies the current selection to clipboard, processes it through an LLM model for official text rewriting,
        and then pastes the processed text back to replace the original selection.

    Arguments:
        None: The function works with the currently selected text in the active application

    Returns:
        None: This function doesn't return any value but modifies the selected text in the active application
    """
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
    """
    Parameters:
        None: This function operates on the current text selection in the active application

    Functionality:
        This function performs a sequence of operations to correct spelling and grammar errors in the selected text.
        It copies the current selection to clipboard, processes it through an LLM model for typo correction,
        and then pastes the corrected text back to replace the original selection.

    Arguments:
        None: The function works with the currently selected text in the active application

    Returns:
        None: This function doesn't return any value but modifies the selected text in the active application
    """
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
