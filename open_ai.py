import requests
from openai import OpenAI
from SECRET import OPENAI_KEY # You have to implement this one ;)

def fetch_image(prompt: str) -> bytes:
    client = OpenAI(api_key=OPENAI_KEY)
    response = client.images.generate(
		model="dall-e-3", prompt=prompt
	)
    # Fetch the image data from the URL
    image_data = requests.get(response.data[0].url).content
    return image_data

# Test code for fetching image
if __name__ == "__main__":
    prompt = input("Enter a prompt for the image: ")
    image_data = fetch_image(prompt)
    
    # Save the image to a file
    with open("output_image.png", "wb") as f:
        f.write(image_data)
    
    print("Image saved as output_image.png")
