from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    print("UrbanNexus System Booting...")
    print(f"Environment: {os.getenv('URBANNEXUS_ENV')}")
    print(f"Log Level: {os.getenv('URBANNEXUS_LOG_LEVEL')}")
    print(f"LangChain Project: {os.getenv('LANGCHAIN_PROJECT')}")

if __name__ == "__main__":
    main()
