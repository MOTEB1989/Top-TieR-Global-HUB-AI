#!/usr/bin/env python3
"""
Quick test script to validate GPT connectivity via OpenAI API.
- Reads API key from environment variable OPENAI_API_KEY
- Sends a simple "Hello" message
- Prints GPT reply or error
"""

import os
import sys
from openai import OpenAI

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OPENAI_API_KEY found in environment.")
        sys.exit(1)

    try:
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",   # أو غيّره حسب الموديل المتاح لك
            messages=[
                {"role": "system", "content": "You are a connection test."},
                {"role": "user", "content": "Hello GPT, are you connected?"}
            ],
            max_tokens=20,
        )

        msg = response.choices[0].message.content.strip()
        print("✅ GPT replied:", msg)

    except Exception as e:
        print("❌ Connection failed:", e)
        sys.exit(2)


if __name__ == "__main__":
    main()
