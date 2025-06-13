from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import mtranslate as mt
import time

# Load the env variables from the .env file
load_dotenv(".env")
InputLanguage = os.getenv("InputLanguage")

# Define the HTML code for the speech recognition interface
HTMLCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language setting in the HTML Code with input language from the environment variables
os.makedirs("Data", exist_ok=True)
with open("Data/Voice.html", "w") as file:
    file.write(HTMLCode)

# Get the current working directory
current_dir = os.getcwd()

# Generate the file path for the HTML file
Link = os.path.join(current_dir, "Data", "Voice.html").replace("\\", "/")

# Set Chrome options for the WebDriver
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")
# Add options to potentially avoid TensorFlow warnings
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-features=VizDisplayCompositor")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
# Disable logging
chrome_options.add_argument("--log-level=3")
# Disable WebGL
chrome_options.add_argument("--disable-webgl")
chrome_options.add_argument("--disable-extensions")

# Initialize the Chrome WebDriver using the ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the path for temporary files
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

# Function to set the assistant's status by writing it to a file
def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "can you", "what's", "where's", "how's"]

    # Check if the query is a question and add a question mark if necessary
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] not in ["?", ".", "!"]:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # Add a period if the query is not a question
        if query_words[-1][-1] not in ["?", ".", "!"]:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# Function to be imported by main.py
def SpeechRecognizer():
    return SpeechRecognition()

# Function to perform speech recognition using the WebDriver
def SpeechRecognition():
    try:
        # Open the HTML file in browser 
        driver.get("file://" + Link)
        # Start speech recognition by clicking the start button 
        driver.find_element(by=By.ID, value="start").click()
        
        # Set a maximum time to wait for speech (in seconds)
        max_wait_time = 60
        start_time = time.time()
        
        while True:
            try:
                # Get the recognized text from the HTML output element
                Text = driver.find_element(by=By.ID, value="output").text
                
                # Check if we've been waiting too long
                if time.time() - start_time > max_wait_time:
                    print("Speech recognition timed out after", max_wait_time, "seconds")
                    driver.find_element(by=By.ID, value="end").click()
                    return "Speech recognition timed out."
                    
                # Check if the text is not empty
                if Text:
                    # Stop recognition by clicking the stop button
                    driver.find_element(by=By.ID, value="end").click()

                    if InputLanguage and (InputLanguage.lower() == "en" or "en" in InputLanguage.lower()):
                        return QueryModifier(Text)
                    else:
                        SetAssistantStatus("Translating....")
                        return QueryModifier(UniversalTranslator(Text))
                
                # Add a short sleep to prevent CPU overload
                time.sleep(0.5)
                    
            except Exception as e:
                print(f"Error during recognition: {e}")
                # Check if we've been waiting too long
                if time.time() - start_time > max_wait_time:
                    print("Speech recognition timed out after", max_wait_time, "seconds")
                    try:
                        driver.find_element(by=By.ID, value="end").click()
                    except:
                        pass
                    return "Speech recognition failed due to an error."
                time.sleep(0.5)
    except Exception as e:
        print(f"Critical error in SpeechRecognition: {e}")
        return "Speech recognition initialization failed."
            
# Main execution block
if __name__ == "__main__":
    # Continuously perform speech recognition and print the recognized text
    Text = SpeechRecognition()
    print(Text)
    