import requests
import numpy as np
import cv2


def img_url_to_array(img_url: str) -> np.array:
    """
    Fetches an image from the given URL and converts it to a NumPy array.

    Parameters:
        img_url (str): URL of the image to fetch.
    
    Returns:
        np.array: NumPy array representing the color image
    """
    
    # Fetch the image from the URL
    response = requests.get(img_url)

    # Read the image from the response content
    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    return img


def test_img_url_to_array(img_url: str = "https://i.scdn.co/image\
/ab6761610000f178133f44ab343b35c715a4ac97"):
    """
    Tests the img_url_to_array function by fetching an image from a specified
    or default test URL, printing its shape, and displaying the image, 

    Parameters:
        img_url (str, optional): URL of the image to test.
            Default URL is a Spotify artist image.
    """
    
    # Run the main function and get image array, then print its shape.
    img_array = img_url_to_array(img_url)
    print(f"Array has shape {img_array.shape}.")

    # Display image
    cv2.imshow("Image", img)


# Run test function if executing this script directly
if __name__ == '__main__':
    test_img_url_to_array()