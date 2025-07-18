from groq import Groq # Importing the Grow library to use its API
from json import load, dump # Importing functions to read and write JSON files
import datetime # Importing the datetime for real-time date and time information
from dotenv import dotenv_values # Importing dotenv_values to read environment variables from a .env file

# Load environment variables from the .env file
env_vars = dotenv_values(".env")
print(f"API Key present: {'GroqAPIKey' in env_vars}")  # Add this line

# Retrieve specific environment variables for username, assistant name, and API key
Username = env_vars.get("Username")
Assistantname = "NOVA"  # Set the assistant name directly
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize an empty list to store chat messages
client = Groq(api_key = GroqAPIKey)

# Initalize an empty list to store chat messages
messages = []

#Define a system message that provides context to AI chatbot about it's role and behaviour
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# A list of system instructions for the chatbot
SystemChatBot = [
    {"role":"system", "content":System}
]

# Attempt to load the chat log from a JSON file
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f) # Load existing messages from the chat log
except FileNotFoundError:
    # If the file doesn't exist, create an empty JSON file to store chat logs
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# Function to get real-time data and time information
def RealtimeInformation():
    current_date_time = datetime.datetime.now() # Get the current date and time
    day = current_date_time.strftime("%A") # Day of the weel
    date = current_date_time.strftime("%d") # Day of the month
    month = current_date_time.strftime("%B") # Full month name
    year = current_date_time.strftime("%Y") # Year
    hour = current_date_time.strftime("%H") # Hour in 24 H format
    minute = current_date_time.strftime("&M") # Minute
    second = current_date_time.strftime("%S") # Second
    
    # Format the information into a String
    data = f"Please use this real-time information if needed, \n"
    data += f"Day: {day}\n Date: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours: {minute} minutes: {second} seconds.\n"
    return data

#Function to modify the chatbot's response for better formatting
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def ChatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response. """
    try: 
        # Load the existing chat log from the JSON file
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
        
        # Append the user's query to the messages list
        messages.append({"role" : "user", "content" : f"{Query}"})

        # Make a request to the Grow API for a response
        print(f"Using model: llama3-70b-8192")  # Update debug line
        completion = client.chat.completions.create(
            model = "llama3-70b-8192",  # This is the correct model name for Llama 3 70B on Groq
            messages = SystemChatBot + [{"role" : "system", "content" : RealtimeInformation()}] + messages, # Include system instructions, real-time infro, and chat history
            max_tokens = 1024, # Limit the maximum tokens in the response 
            temperature = 0.7, # Adjust response randomness (higher means more random)
            top_p = 1, # Use nucleus sampling to control diversity
            stream = True, # Enable streaming response 
            stop = None # Allow the model to determine when to stop 
        )

        # Initialize an empty string to store the AI's response
        Answer = ""

        # Process the streamed response chunks
        for chunk in completion:
            if chunk.choices[0].delta.content: # Check if there's content in the current chunk
                Answer += chunk.choices[0].delta.content # Append the content to the answer

        # Clean up any unwanted tokens from the response
        Answer = Answer.replace("</s>", "")

        # Append the chatbot's response to the messages list 
        messages.append({"role" : " assistant", "content" : Answer})

        # Save the updated chat log to the JSON file
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent = 4)

        # Return the formatted response
        return AnswerModifier(Answer = Answer)
    
    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent = 4)
        return "Sorry, I encountered an error. Please check your API key and internet connection."  # Return error message instead of retrying
    
# Main program entry point
if __name__ == "__main__":
    while(True):
        user_input = input("Enter your Question: ") # Prompt the user for a question
        print(ChatBot(user_input)) # Call the ChatBot function and print its response

# Function to be imported by main.py
def Chatbot(Query):
    return ChatBot(Query)