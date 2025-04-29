from src.chatbot.message_handler import ChatbotMessageHandler
from src.database.operations import create_tables
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the nutrition tracking chatbot application."""
    logger.info("Starting Nutrition Tracker Chatbot")
    
    # Initialize database
    create_tables()
    
    # Initialize chatbot
    chatbot = ChatbotMessageHandler()
    
    print("Welcome to your Nutrition Tracking Assistant!")
    print("Type 'exit' to quit, 'help' for commands.")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'exit':
            print("Goodbye! Keep up the good work on your fitness journey!")
            break
            
        response = chatbot.handle_message(user_input)
        print(f"\nNutrition Assistant: {response}")

if __name__ == "__main__":
    main()