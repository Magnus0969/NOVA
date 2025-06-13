from webbrowser import open as webopen  # Import web browser functionality
from AppOpener import close, open as appopen  # Import functions to open and close apps
from pywhatkit import search, playonyt  # Import functions for Google search and YouTube playback
from dotenv import dotenv_values  # Import dotenv to manage environmental variables
from bs4 import BeautifulSoup  # Import BeautifulSoup for HTML parsing
from groq import Groq  # Import Groq to use it's AI model
import webbrowser  # Import webbrowser for opening URLs
import subprocess  # Import subprocess for interacting with system
import requests  # Import requests for making HTTP request
from rich import print # Import rich Styled console output
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume # Import pycaw for controlling system volume
import ctypes
import os  # Import os for Operating System functionalities
import keyboard  # Import keyboard for keyboard related actions
import asyncio  #Import asyncio for asynchronous programming

# Load env variables from .env file
env_vars= dotenv_values(".env")
GroqAPIkey= env_vars.get("GroqAPIKey") # Retrieve the Groq API Key

# Create Groq Client with API Key
client= Groq(api_key=GroqAPIkey)

# Define user agent for making web requests
user_agent = "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# Define CSS classes for parsing specific elements in HTML content
css_classes=[
    "zCubwf", "hgKELc", "LTKOO sY7ric","Z0LcW","gsrt vk_bk FzvWSb YwPhnf", "pclqee","tw-Data-text tw-text-small tw-ta",
    "IZ6rdc", "05uR6d LTKOO" , "vlzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb4Bb gsrt",
    "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

# Predefined professional responses for user interaction
prof_response = [
    "Thank you for reaching out! I'm here to assist you with any questions or concerns.",
    "Please let me know how I can further assist you; your satisfaction is my priority.",
    "I'm glad to help! If there's anything else you need, don't hesitate to ask.",
    "Your concerns are important to me; I'm here to provide the support you need.",
    "Thank you for your patience; I'm working to resolve this as quickly as possible.",
    "If you have any additional questions, feel free to ask anytime.",
    "I strive to provide the best assistance; let me know how I can improve.",
    "Let me know if there's anything specific you'd like to know; I'm here to help!"
]

messages=[]  # List to store Chatbot messages

# System message to provide context to the Chatbot
system_chatbot=[{"role":"system","content" : f"Hello I am {os.environ.get('Username')}, You're NOVA, an advanced content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# Function to perform a Google Search
def GoogleSearch(Topic):
    search(topic=Topic)  # Use pywhatkit's search function to perform a Google search.
    return True  # Successfull

# Function to generate content using AI and saving it in a file
def Content(Topic):
    # Nested Function to open a file in notepad
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor,File])
    
    # Nested Function to gnerate content using AI chatbot
    def ContentWriter(prompt):
        messages.append({"role":"user","content":f"{prompt}"})  # Add user prompt to messages

        completion= client.chat.completions.create(
            model="llama3-70b-8192",  # Specify the AI model
            messages= system_chatbot + messages,  # Include System Instructions and Chat History
            max_tokens= 2048,  # maximum tokens in response
            temperature=0.7,  # response randomness or creativity level
            top_p=1,  # Nucleus sampling for response diversity
            stream= True,  # Show response as they are generated
            stop= None  # Allow the model to determine stopping condition
        )

        Answer = "" # Empty string to store response

        # Process streamed response
        for chunk in completion:
            if chunk.choices[0].delta.content:  # Check the content in current chunk
                Answer+= chunk.choices[0].delta.content  # Append the content to the answer
        
        Answer= Answer.replace("</s>","")  # Remove unwanted tokens from the response
        messages.append({"role": "assistant","content": Answer}) # Add the AI's response to messeges
        return Answer
    Topic: str = Topic.replace("Content ","")  # Remove "Content" from the topic
    AI_CONTENT= ContentWriter(Topic)  # Generate content using AI

    # Save the generated content to a file
    with open(rf"Data\{Topic.lower().replace(' ','')}.txt","w",encoding="utf-8") as file:
        file.write(AI_CONTENT) # Write the content to a file
        file.close()

    OpenNotepad(rf"Data\{Topic.lower().replace(' ','')}.txt") # Open the file in Notepad
    
    return True # Indicate success

# Function to search for a topic on YouTube
def YouTubeSearch(Topic):

    search_url = f"https://www.youtube.com/results?search_query={Topic}"  # Construct the YouTube search URL
    webbrowser.open(search_url)  # Open the URL on web browser
    
    return True  # Successfull

# Function to play a video on YouTube
def YoutubePlay(query):

    playonyt(query)  # pywhatkit's playonyt function plays a youtube video

    return True

# Function to open an application
def OpenApp(app, sess=requests.session()):
    try:
        # Attempt to open the app
        appopen(app, match_closest=True, throw_error=True, output=True)
        return True  # Successfully opened the app

    except:

        # Nested function to extract links from Google search results
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')  # Parse the HTML content
            links = soup.find_all('a', {'jsname': 'UWckNb'})  # Find relevent links
            
            return [link.get('href') for link in links] # Return the links

        # Nested function to perform a Google search and retrieve results
        def search_google(query):
            url = f"https://www.google.com/search?q={query}"  # Construct the Google search URL
            headers = {"User-Agent": user_agent}  # Using pre-defined user agent
            response = sess.get(url, headers=headers)  # Performing GET request

            if response.status_code == 200:
                return response.text  # Return HTML content of the Google search page
            else:
                print("Failed to retrieve search results.")
            return None

        # Perform the Google search
        html = search_google(app)

        if html:
            links = extract_links(html)[0]  # Extract the first link from the search results 
            webopen(links) # Open the link in web browser
        
        return True
    print(f"Opening {app}")

# Function to close an application
def CloseApp(app):

    if "chrome" in app:
        pass  # Skip if the app is chrome
    else:
        try:
            close(app, match_closest=True, output=True,throw_error=True)
            return True  # Success
        except:
            return False  # Failed

# Function to execute system level commands
def System(command):
    # Nested Function to mute system volume
    def mute_unmute():
        keyboard.press_and_release("volume mute")  # Stimulate the mute key press
    
    # Nested Function to decrease system volume
    def vol_down():
        keyboard.press_and_release("volume down")  # Stimulate the volume down key press
    
    # Nested Function to increase system volume
    def vol_up():
        keyboard.press_and_release("volume up")  # Stimulate the volume up key press
    
    # Nested Function to set system volume to a specific level
    def vol_set(level):
        try:
            # Fetch all audio sessions
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                # Set the volume level (0.0 to 1.0)
                volume.SetMasterVolume(level / 100.0, None)
            print(f"Volume set to {level}%")
        except Exception as e:
            print(f"Failed to set volume: {e}")
    
    # Execute the appropriate commands
    if command == "mute":
        mute_unmute()
    elif command == "unmute":
        mute_unmute()
    elif command == "volume up":
        vol_up()
    elif command == "volume down":
        vol_down()
    elif command.startswith("volume set "):
        try:
            # Extract the desired volume level from the command
            level = int(command.removeprefix("volume set ").strip())
            if 0 <= level <= 100:
                vol_set(level)
            else:
                print("Volume level must be between 0 and 100.")
        except ValueError:
            print("Invalid volume level provided.")
    
    return True  # Success
# Asynchronous Function to translate and execute user command
async def TranslateAndExecute(commands: list[str]):
    
    funcs=[]  # List to store asynchronous task
    for command in commands:

        # Handle "open" commands
        if command.startswith("open "):
            
            if "open it " in command:
                pass  # Ignore open it command

            if "open file " in command:
                pass  # Ignore open file command
            else:
                func= asyncio.to_thread(OpenApp, command.removeprefix("open ")) # Schedule app opening
                funcs.append(func)  # Append the performed function to funcs list
       
        elif command.startswith("close "):
            func= asyncio.to_thread(CloseApp, command.removeprefix("close ")) # Schedule app closing
            funcs.append(func)  # Append the performed function to funcs list

        elif command.startswith("general"):
            pass # Ignore general commands

        elif command.startswith("realtime"):
            pass # Ignore real-time commands

        elif command.startswith("play on youtube "):
            func= asyncio.to_thread(playonyt, command.removeprefix("play ")) # Schedule YouTube playing
            funcs.append(func)  # Append the performed function to funcs list
        
        elif command.startswith("content "):
            func= asyncio.to_thread(Content, command.removeprefix("content ")) # Schedule content creation
            funcs.append(func)  # Append the performed function to funcs list
        
        elif command.startswith("google search "):
            func= asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")) # Schedule Google search
            funcs.append(func)  # Append the performed function to funcs list
        
        elif command.startswith("youtube search "):
            func= asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")) # Schedule YouTube search
            funcs.append(func)  # Append the performed function to funcs list
        
        elif command.startswith("system "):
            func= asyncio.to_thread(System, command.removeprefix("system ")) # Schedule system command
            funcs.append(func)  # Append the performed function to funcs list
        
        else:
            print(f"No function found for {command}")  # Print an error for unknown commands
    
    results= await asyncio.gather(*funcs)  # Execute all tasks concurrently

    # Process the result
    for result in results:
        if isinstance(result,str):
            yield result
        else:
            yield result

# Asynchronous Function to automate command execution
async def Automation(commands: list[str]):

    async for result in TranslateAndExecute(commands=commands):
        pass  # Translate and Execute commands

    return True  # Success