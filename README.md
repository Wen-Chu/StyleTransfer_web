# Image Style Transfer

Introduction
---
- This is a web application based on Flask and TensorFlow for combining the style and content of two images. 
- Users can upload images or provide URLs for them, where one serves as the 'content image' and the other as the 'style image'. 
- The application uses a deep learning model to apply the artistic style of the style image to the content image, creating a unique, stylized composite.
  - Reference of Style Transfer：[Fast Style Transfer for Arbitrary Styles](https://www.tensorflow.org/hub/tutorials/tf2_arbitrary_image_stylization)


Features
---
- Upload images or provide images through URLs.
- Perform style transfer on uploaded images.
- Display the original and style-transferred images.
- Download the transformed image.

How to Run
---
1. Install the required packages.
    ```
    pip install -r requirements.txt
    ```
2. Create a folder names 'Images' in the static folder.
3. Run the application.
    ```
    python app.py
    ```