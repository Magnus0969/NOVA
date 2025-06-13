import asyncio
import os
import random
import requests
from PIL import Image
from time import sleep
from dotenv import get_key

# Function to open and display images based on a given prompt
def open_image(prompt):
    folder_path= r"Data" # Folder where images are stored
    prompt = prompt.replace(" ", "_")  # Replace spaces with underscores

    # Generate filenames for the images
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            # Try to open and display the image
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Pause for 1 sec before showing the next
        
        except IOError:
            print(f"Error: Could not open image {image_path}")

# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers= {"Authorization": f"Bearer {get_key('.env','HuggingFaceAPI')}"}

# Async function to send a query to Hugging Face API
async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.content
    except Exception as e:
        print(f"API Error: {e}")
        return None  # Return None in case of errors

# Async function to generate image based on given prompt
async def generate_images(prompt: str):
    tasks = []

    # Create 2 image generation tasks
    for _ in range(2):
        payload= {
            "inputs": f"{prompt}, quality: 4K, sharpness= high, realistic, cinematic, 8k, HDR,ultra-detailed, high-definition, high resolution, seed={random.randint(0, 1000000)}",
            }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
    
    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)

    # Save the generated images to files
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes is None:
            print(f"Skipping image {i+1} due to API error")
            continue
            
        file_path = fr"Data\{prompt.replace(' ', '_')}{i+1}.jpg"
        try:
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            print(f"Saved image to {file_path}")
        except Exception as e:
            print(f"Error saving image {i+1}: {e}")

# Wrapper function to generate and open images
def GenerateAndOpenImages(prompt):
    # Ensure Data directory exists
    os.makedirs("Data", exist_ok=True)
    
    asyncio.run(generate_images(prompt))  # Run the async function to generate images
    open_image(prompt)  # Open the generated images

# Main loop to monitor image generation requests
while True:

    try:
        # Read the status and prompt from the data file
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data = f.read()
        
        Prompt, Status = Data.split(",")
        Status = Status.strip()  # Remove any whitespace

        if Status == "True":
            # If status is True, generate and open images
            print(f"Generating Images for prompt: {Prompt}")
            GenerateAndOpenImages(prompt=Prompt)

            # Reset the status in the file after generating images
            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")
                break
        else:
            # If status is False, wait for a while before checking again
            print("Waiting for Image Generation...")
            sleep(1)
    
    except Exception as e:
        # Handle any exceptions that occur during the process
        print(f"Error: {e}")