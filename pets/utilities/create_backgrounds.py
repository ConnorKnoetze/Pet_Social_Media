from PIL import Image
import os


def create_backgrounds():
    sizes = [
        # Mobile (portrait)
        (320, 568),  # iPhone SE (1st gen)
        (375, 667),  # iPhone 6, 7, 8
        (390, 844),  # iPhone 12, 13
        (393, 852),  # iPhone 14, 15
        (414, 896),  # iPhone 11, XR, XS Max
        (360, 640),  # Common Android
        (412, 915),  # Larger Android
        # Mobile (landscape)
        (667, 375),
        (896, 414),
        # Tablets
        (768, 1024),  # iPad portrait
        (1024, 768),  # iPad landscape
        (800, 1280),  # Android tablet
        # Desktop/Laptop
        (1366, 768),  # Common laptop
        (1440, 900),  # MacBook Air
        (1536, 864),  # Common laptop
        (1600, 900),  # 16:9 HD+
        (1920, 1080),  # Full HD
        (2560, 1440),  # QHD/2K
        (3440, 1440),  # Ultrawide QHD
        (3840, 2160),  # 4K UHD
    ]

    ABS_INPUT_FILE_LIGHT = os.path.abspath(
        "pets/static/images/backgrounds/light_back_full4k.png"
    )
    ABS_INPUT_FILE_DARK = os.path.abspath(
        "pets/static/images/backgrounds/dark_back_full4k.png"
    )

    for size in sizes:
        width, height = size

        # Process light image
        image_light = Image.open(ABS_INPUT_FILE_LIGHT)

        # Calculate scale to cover target size (maintain aspect, resize to fit smallest dimension)
        scale = max(width / image_light.width, height / image_light.height)
        new_width = int(image_light.width * scale)
        new_height = int(image_light.height * scale)

        # Resize with high quality
        resized_light = image_light.resize(
            (new_width, new_height), Image.Resampling.LANCZOS
        )

        # Crop from center to exact target size
        left = (new_width - width) // 2
        top = (new_height - height) // 2
        background_light = resized_light.crop((left, top, left + width, top + height))

        # Process dark image
        image_dark = Image.open(ABS_INPUT_FILE_DARK)
        resized_dark = image_dark.resize(
            (new_width, new_height), Image.Resampling.LANCZOS
        )
        background_dark = resized_dark.crop((left, top, left + width, top + height))

        # Save the images
        abs_output_dir_light = os.path.abspath(
            f"pets/static/images/backgrounds/light/{width}"
        )
        abs_output_dir_dark = os.path.abspath(
            f"pets/static/images/backgrounds/dark/{width}"
        )
        os.makedirs(abs_output_dir_light, exist_ok=True)
        os.makedirs(abs_output_dir_dark, exist_ok=True)

        background_light.save(
            os.path.join(abs_output_dir_light, f"light_back_{width}x{height}.png"),
            optimize=True,
        )
        background_dark.save(
            os.path.join(abs_output_dir_dark, f"dark_back_{width}x{height}.png"),
            optimize=True,
        )
