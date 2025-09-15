import openai

def thread_to_conversation(thread_id: str):
    """Convert a thread's messages to a conversation."""
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
