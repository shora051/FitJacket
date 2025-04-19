import os
import time
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler('gemini_api.log')  # Output to file
    ]
)
logger = logging.getLogger('gemini_api')

# Gemini API key from environment variables
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Configure Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
else:
    logger.error("GEMINI_API_KEY not found in environment variables!")

def get_gemini_response(query):
    """Get a response from Gemini API with detailed logging"""
    if not GEMINI_API_KEY:
        logger.error("No Gemini API key available")
        return None, "API key not configured"
    
    start_time = time.time()
    logger.info(f"Sending query to Gemini API: '{query}'")
    
    try:
        # Configure the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Set up a fitness-focused system prompt
        system_prompt = """
        You are FitJacket's fitness assistant. Provide helpful, concise advice on fitness, 
        workouts, exercises, nutrition, and recovery. Keep responses under 150 words, 
        focus on evidence-based information, and avoid medical advice. 
        Be friendly and encouraging.
        """
        
        # Create chat with system prompt
        chat = model.start_chat(history=[
            {
                "role": "user",
                "parts": [{"text": system_prompt}]
            },
            {
                "role": "model", 
                "parts": [{"text": "I'll be your friendly fitness assistant, providing concise, evidence-based advice about workouts, exercises, nutrition, and recovery. How can I help you today?"}]
            }
        ])
        
        # Get response from Gemini
        response = chat.send_message(query)
        
        # Log the successful response
        execution_time = time.time() - start_time
        logger.info(f"Gemini API response received in {execution_time:.2f}s")
        logger.debug(f"Gemini response: {response.text}")
        
        return response.text, None
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_message = str(e)
        
        logger.error(f"Gemini API error in {execution_time:.2f}s: {error_message}")
        logger.error(f"Query that caused the error: '{query}'")
        
        # Add more detailed debugging for specific errors
        if "rate limit" in error_message.lower():
            logger.error("Rate limit exceeded for Gemini API")
        elif "invalid request" in error_message.lower():
            logger.error("Invalid request format")
        elif "api key" in error_message.lower():
            logger.error("API key issue with Gemini")
            
        return None, error_message

# Fallback responses if Gemini API is unavailable
FALLBACK_RESPONSES = {
    "hello": "Hello! I'm your FitJacket assistant. How can I help with your fitness journey today?",
    "general": "I'm your FitJacket fitness assistant! You can ask me about workouts, specific exercises, nutrition, recovery, or fitness tips."
}