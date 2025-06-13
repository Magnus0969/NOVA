from googlesearch import search # Importing googlesearch to search the web
from groq import Groq # Importing groq to use groq api
from json import load, dump # Importing load and dump to read and write json files
import datetime # Importing datetime to get the current date and time
from dotenv import dotenv_values # Importing gotenv_values to read environment variables

# Loading environment variables
env_vars = dotenv_values(".env")

# Retrieve specific environment variables for username, assistant name, and API key
Username = env_vars.get("Username")
Assistantname = "NOVA"  # Set the assistant name directly
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize an empty list to store chat messages
client = Groq(api_key = GroqAPIKey)


# Define a system message that provides context to AI chatbot about it's role and behaviour
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Attempt to load the chat log from a JSON file
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f) # Load existing messages from the chat log
except:
    # If the file doesn't exist, create an empty JSON file to store chat logs
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# Function to perfrom a Google Search and format results
def GoogleSearch(Query):
    results = list(search(Query, advanced=True, num_results = 5)) # Perform a Google search and get the top 5 results
    Answer = f"The search results for '{Query}' are:\n[start]\n"
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

# Function to clean up answer by removing empty lines and extra spaces
def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

# Predefnied chatbot conversation system message and an initial user message
SystemChatBot = [
    {'role':'system', 'content':System},
    {'role':'user', 'content':'Hi'},
    {'role':'assistant', 'content':'Hello, How can I help you?'}
]

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
    
# Function to handle realtime search and response generation - this is the function imported by main.py
def RealtimeSearchEngine(prompt):
    return RealtimeSearch(prompt)

# Function to handle realtime search and response generation
def RealtimeSearch(prompt):
    global SystemChatBot, messages

    # Load the chat history from the JSON file
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)

    messages.append({'role':'user', 'content':f"{prompt}"})

    # Add Google search results to the messages
    SystemChatBot.append({'role':'system', 'content':GoogleSearch(prompt)})
    # Generate a response using the groq client
    completion = client.chat.completions.create(
        model="llama3-70b-8192",  # This is the correct model name for Llama 3 70B on Groq
        messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,  # Include system instructions, real-time info, and chat history
        max_tokens=2048,  # Limit the maximum tokens in the response
        temperature=0.7,  # Adjust response randomness (higher means more random)
            top_p = 1, # Use nucleus sampling to control diversity
            stream = True, # Enable streaming response 
            stop = None # Allow the model to determine when to stop 
        )
    
    # Initialize an empty string to store the AI's response
    Answer = ""

    # Concantenate response chunks from the streaming output
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    # Clean up the response
    Answer = Answer.strip().replace("</s>", "")
    messages.append({'role':'assistant', 'content':Answer})

    # Save the updated chatlog back to the JSON file
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent = 4)

    # Remove the most recent system message from the chatbot conversation
    SystemChatBot.pop()
    return AnswerModifier(Answer = Answer)

# Main entry point of the program for interactive querying
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearch(prompt))


    
    
            
