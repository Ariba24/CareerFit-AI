
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERROR: GOOGLE_API_KEY was not found in .env")
else:
    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0,
        )

        response = model.invoke(
            "Reply with exactly these words: Gemini connection successful!"
        )

        print("\nSUCCESS:", response.content)

    except Exception as error:
        print("\nCONNECTION ERROR:", error)
