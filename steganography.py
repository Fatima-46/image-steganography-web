"""
Image Steganography Tool (LSB Technique)
------------------------------------------
What this does:
  Hides a secret text message inside a PNG image so that the image
  looks completely normal, but the tool can extract the hidden text
  back out later.

The core idea (Least Significant Bit / LSB):
  Every pixel in an image is made of Red, Green, and Blue values,
  each stored as an 8-bit number from 0-255 (e.g. 200 = 11001000).

  The LAST bit of that number (the "least significant bit") barely
  affects the color at all -- changing 200 (11001000) to 201 (11001001)
  is a difference the human eye cannot detect.

  So: we take our secret message, convert it to binary (0s and 1s),
  and hide ONE bit of our message inside the last bit of each pixel's
  color value. The image looks unchanged, but the bits are all there
  if you know how to read them back out.

Why PNG (not JPG):
  JPG compresses images in a "lossy" way that can scramble our hidden
  bits. PNG is lossless, so every bit we hide stays exactly where we
  put it.
"""

from PIL import Image

# A special marker so the decoder knows where the hidden message ends.
END_MARKER = "#####"


def text_to_binary(text):
    """
    Convert a string into a single string of 0s and 1s (8 bits per BYTE,
    not per character). We encode to UTF-8 first so that any character -
    including em dashes, accented letters, emojis, etc. - always maps to
    a whole number of 8-bit bytes. (A previous version used ord(char)
    directly, which breaks for any character outside the 0-255 range.)
    """
    utf8_bytes = text.encode('utf-8')
    return ''.join(format(byte, '08b') for byte in utf8_bytes)


def binary_to_text(binary):
    """Convert a string of 0s and 1s back into readable text (UTF-8 decode)."""
    # Only take full 8-bit groups; drop any leftover bits at the end.
    usable_len = len(binary) - (len(binary) % 8)
    byte_values = [int(binary[i:i+8], 2) for i in range(0, usable_len, 8)]
    return bytes(byte_values).decode('utf-8', errors='ignore')


def encode_image(input_image_path, secret_message, output_image_path):
    """
    Hides `secret_message` inside `input_image_path` and saves the
    result as `output_image_path`.
    """
    image = Image.open(input_image_path)
    image = image.convert("RGB")  # make sure we have clean R,G,B values

    # Add our end marker so decoding knows when to stop reading bits
    message_with_marker = secret_message + END_MARKER
    binary_message = text_to_binary(message_with_marker)

    total_pixels = image.width * image.height
    if len(binary_message) > total_pixels * 3:
        raise ValueError(
            "Message too long to hide in this image. Use a bigger image "
            "or a shorter message."
        )

    encoded_image = image.copy()
    pixels = encoded_image.load()

    bit_index = 0
    binary_len = len(binary_message)

    for y in range(image.height):
        for x in range(image.width):
            if bit_index >= binary_len:
                break

            r, g, b = pixels[x, y]
            # For each color channel, replace the LAST bit with our
            # message bit (if we still have message bits left to hide).
            if bit_index < binary_len:
                r = (r & ~1) | int(binary_message[bit_index])
                bit_index += 1
            if bit_index < binary_len:
                g = (g & ~1) | int(binary_message[bit_index])
                bit_index += 1
            if bit_index < binary_len:
                b = (b & ~1) | int(binary_message[bit_index])
                bit_index += 1

            pixels[x, y] = (r, g, b)

        if bit_index >= binary_len:
            break

    encoded_image.save(output_image_path, "PNG")
    print(f"Message hidden successfully -> {output_image_path}")


def decode_image(encoded_image_path):
    """
    Reads an image that was created with encode_image() and extracts
    the hidden text message.
    """
    image = Image.open(encoded_image_path)
    image = image.convert("RGB")
    pixels = image.load()

    binary_message = ""

    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y]
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)

    # Convert all the bits back to text, then cut it off at our marker
    decoded_text = binary_to_text(binary_message)
    end_index = decoded_text.find(END_MARKER)

    if end_index == -1:
        return "No hidden message found (or this image wasn't encoded with this tool)."

    return decoded_text[:end_index]


if __name__ == "__main__":
    print("=== Image Steganography Tool ===")
    print("1. Hide a message in an image")
    print("2. Extract a message from an image")
    choice = input("Choose an option (1 or 2): ").strip()

    if choice == "1":
        input_path = input("Path to source image (e.g. cover.png): ").strip()
        message = input("Secret message to hide: ").strip()
        output_path = input("Output filename (e.g. secret.png): ").strip()
        encode_image(input_path, message, output_path)

    elif choice == "2":
        encoded_path = input("Path to encoded image (e.g. secret.png): ").strip()
        hidden_message = decode_image(encoded_path)
        print(f"\nHidden message: {hidden_message}")

    else:
        print("Invalid choice.")
