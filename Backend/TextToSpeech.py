import pygame # Importing pygame for handling audio playback
import random # Importing random for generating random choices
import asyncio # Importing asyncio for handling asynchronous operations
import os # Importing os for handling file operations
import edge_tts # Importing edge_tts for text-to-speech
from dotenv import load_dotenv # Importing dotenv for handling environment variables

# Load environment variables from a .env file
load_dotenv(".env")
# Set default voice if not found in environment variables
AssistantVoice = os.getenv("AssistantVoice", "en-US-JennyNeural")  # Default voice for NOVA

# Create Data directory if it doesn't exist
os.makedirs("Data", exist_ok=True)

# Asynchronous function to convert text to an audio file
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"
    
    if os.path.exists(file_path): # Check if file exists 
        os.remove(file_path) # If it already exists, remove it to avoid overwriting errors

    try:
        # Create the communication object to generate speech
        communicate = edge_tts.Communicate(text, AssistantVoice, pitch="+5Hz", rate="+13%")
        await communicate.save(file_path) # Save the generated speech to the file
    except Exception as e:
        print(f"Error in TextToAudioFile: {e}")
        raise

# Function to handle Text-To-Speech(TTS) functionality
def TTS(Text, func = lambda r = None : True):
    try:
        # Convert text to an audio file asynchronously
        asyncio.run(TextToAudioFile(Text))

        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

        # Check if the file exists before trying to load it
        if not os.path.exists(r"Data\speech.mp3"):
            print("Speech file was not created")
            return False

        # Load the generated speech file into pygame mixer 
        pygame.mixer.music.load(r"Data\speech.mp3") 
        pygame.mixer.music.play() # Play the generated speech

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            if func() == False:
                break
            pygame.time.Clock().tick(10) # Limit the loop to 10 ticks per second
        return True
    except Exception as e: # Handle any exceptions that occur
        print(f"Error in TTS: {e}")
        return False
    finally:
        try:
            # Call the provided function with False to signal at the end of TTS 
            func(False)
            # Only stop and quit if mixer is initialized
            if pygame.mixer.get_init():
                pygame.mixer.music.stop() # Stop the audio playback
                pygame.mixer.quit() # Quit the mixer
        except Exception as e:
            print(f"Error in finally block: {e}")

# Function to manage Text-To-Speech with additional responses for long text
def TextToSpeech(Text, func = lambda r = None : True):
    Data = str(Text).split(".")

    # List of predefined responses for cases where the text is too long
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    # If the text is very long (more than 4 sentences and 250 characters), add a response message
    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
    # Otherwise, just play the whole text
    else:
        TTS(Text, func)

# Main execution loop
if __name__ == "__main__":
    while True:
        # Prompt user for input and pass it to TextToSpeech function 
        TextToSpeech(input("Enter the text: "))