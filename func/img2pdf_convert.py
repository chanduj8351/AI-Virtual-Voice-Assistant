import os
import img2pdf


def img2pdf_converter(image_paths: list[str], file_name: str, file_size: int = 50, destination_path: str = os.getcwd() + "\\data\\pdfs\\"):
    """
    Converts multiple image files into a single PDF file.

    Args:
        image_paths (list[str]): A list of image file paths to be converted.
        file_name (str): The desired name for the output PDF file.
        file_size (int, optional): JPEG quality (1 to 100, applicable to JPEG images). Default is 50.
        destination_path (str, optional): The folder where the PDF file will be saved. Default is "C:\\Users\\chand\\Desktop\\Siri17\\web\\".

    Raises:
        FileNotFoundError: If any image file is missing.
        ValueError: If `image_paths` is empty or `file_size` is out of range.
    """

    # Validate inputs
    if not image_paths:
        raise ValueError("The image_paths list cannot be empty.")

    if not (1 <= file_size <= 100):
        raise ValueError("file_size must be between 1 and 100.")

    # Check if all images exist
    for image_path in image_paths:
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"The file '{image_path}' does not exist.")

    # Ensure the destination path exists
    os.makedirs(destination_path, exist_ok=True)

    output_path = os.path.join(destination_path, f"{file_name}.pdf")

    # Convert images to PDF
    try:
        with open(output_path, "wb") as pdf_file:
            pdf_file.write(img2pdf.convert(image_paths, jpeg_quality=file_size))
        print("✅ PDF created successfully at:", output_path)
    except Exception as e:
        print("❌ Error while creating PDF:", e)


if __name__ == "__main__":
    img2pdf_converter(image_paths=['1.jpg'], file_name='t5', file_size=70)
