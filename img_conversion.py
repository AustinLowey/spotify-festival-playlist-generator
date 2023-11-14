import requests
import numpy as np
import cv2

def img_url_to_array(img_url: str, display_img=False) -> np.array:
    # Fetch the image from the URL
    response = requests.get(img_url)

    # Read the image from the response content
    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # Display image (primarily for testing/verification)
    if display_img == True:
        cv2.imshow("Image", img)

    return img # np.array with shape (160, 160, 3)


def test_img_url_to_arr(img_url = "https://i.scdn.co/image\
/ab6761610000f178133f44ab343b35c715a4ac97"):
    img_array = img_url_to_arr(img_url, display_img=True)
    print(f"Array has shape {img_array.shape}.")
