from typing import List
from modules.assistant_config import get_config
from modules.base_assistant import PlainAssistant
from modules.utils import create_session_logger_id, setup_logging
import typer
import logging
import sys

app = typer.Typer()


@app.command()
def ping():
    print("pong")


@app.command()
def chat():
    """Start a text-only chat session with Sam"""
    # Create session and logging
    session_id = create_session_logger_id()
    logger = setup_logging(session_id)
    logger.info(f"[START] Starting chat session {session_id}")

    # Create assistant
    assistant = PlainAssistant(logger, session_id)
    
    # Display greeting from personality engine
    if assistant.personality_engine:
        greeting = assistant.personality_engine.get_greeting()
        print(f"\nSam: {greeting}\n")
        logger.info(f"[PERSONALITY] Greeting: {greeting}")

    print("(Type 'exit', 'quit', or 'bye' to end)\n")
    
    try:
        while True:
            try:
                # Get text input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                text_lower = user_input.lower()
                if text_lower in ["exit", "quit", "bye"]:
                    logger.info("[EXIT] User requested exit")
                    print("\nSam: Bye! Take care.\n")
                    
                    # Clean up resources
                    try:
                        if hasattr(assistant, 'cleanup'):
                            assistant.cleanup()
                    except Exception as e:
                        logger.error(f"[ERROR] Cleanup error: {str(e)}")
                    
                    logger.info("[EXIT] Clean shutdown complete")
                    sys.exit(0)
                
                # Process input and get response
                response = assistant.process_text(user_input)
                logger.info(f"[ASSISTANT] Response: {response}")
                
                # Print response
                if response:
                    print(f"\nSam: {response}\n")
            
            except KeyboardInterrupt:
                logger.info("[EXIT] Session interrupted by user (Ctrl+C)")
                print("\n\nSam: Goodbye! Shutting down...")
                
                # Clean up resources
                try:
                    if hasattr(assistant, 'cleanup'):
                        assistant.cleanup()
                except:
                    pass
                
                print("Shutdown complete.")
                logger.info("[EXIT] Clean shutdown complete")
                sys.exit(0)
            
            except Exception as e:
                logger.error(f"[ERROR] Error occurred: {str(e)}")
                print(f"Error: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"[ERROR] Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    app()
