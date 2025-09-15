"""
This script provides a utility to convert the messages from an OpenAI thread
into a conversation format using the OpenAI API.

Usage:
    Run this script directly to convert a specific thread by its ID and print the resulting conversation.

Requirements:
    - openai Python package
    - Proper OpenAI API credentials configured in your environment
"""
import openai

def thread_to_conversation(thread_id: str):
    """
    Convert a thread's messages to a conversation using the OpenAI API.

    Args:
        thread_id (str): The ID of the OpenAI thread whose messages are to be converted.

    Returns:
        openai.resources.conversation.Conversation: The created conversation object as returned by the OpenAI API.

    Raises:
        openai.error.OpenAIError: If an error occurs while communicating with the OpenAI API.
        Exception: For any other unexpected errors.

    Note:
        This function requires valid OpenAI API credentials to be set in your environment.
    """
    messages = []
    for page in openai.beta.threads.messages.list(
        thread_id=thread_id, order="asc"
    ).iter_pages():
        messages.extend(page.data)

    items = []
    for m in messages:
        content_items = []
        for content in m.content:
            if content.type == "text":
                item_type = "input_text" if m.role == "user" else "output_text"
                content_items.append({"type": item_type, "text": content.text.value})
            elif content.type == "image_url":
                content_items.append(
                    {
                        "type": "input_image",
                        "image_url": content.image_url.url,
                        "detail": content.image_url.detail,
                    }
                )
        items.append({"role": m.role, "content": content_items})

    return openai.conversations.create(items=items)


if __name__ == "__main__":
    conversation = thread_to_conversation("thread_EIpHrTAVe0OzoLQg3TXfvrkG")
    print(conversation)
