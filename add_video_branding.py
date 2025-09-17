#!/usr/bin/env python3
"""
Single clean script for adding branding to videos:
- Logo: Top left, 60% transparency
- Text box: Full width at bottom, 50% black background
- Text: White text centered in bottom box
"""

import subprocess
import os
import sys

def add_video_branding(input_video, logo_path, text, output_video):
    """
    Add branding to video with clean layout

    Args:
        input_video: Path to input video file
        logo_path: Path to logo PNG file
        text: Text to display
        output_video: Path for output video file
    """

    # Transparency settings
    logo_alpha = 0.8   # 80% opacity for logo (less transparent)
    box_alpha = 0.3    # 30% opacity for black text box (less transparent)
    text_alpha = 0.9   # 90% opacity for text

    # Layout settings
    box_height = 80

    # FFmpeg filter: Logo top-left, transparent black box at true bottom with text
    # Box at y=1000 (1080-80=1000), text centered both horizontally and vertically
    filter_complex = (
        f'[1:v]format=rgba,colorchannelmixer=aa={logo_alpha}[logo_alpha];'
        f'[0:v][logo_alpha] overlay=10:10 [with_logo];'
        f'[with_logo] drawbox=x=0:y=1000:w=iw:h=80:color=black@{box_alpha}:t=fill [with_box];'
        f'[with_box] drawtext=text=\'{text}\':fontsize=36:fontcolor=white@{text_alpha}:x=(w-text_w)/2:y=1000+(80-text_h)/2'
    )

    cmd = [
        'ffmpeg',
        '-i', input_video,
        '-i', logo_path,
        '-filter_complex', filter_complex,
        '-codec:a', 'copy',
        '-y',
        output_video
    ]

    print(f"Adding branding to: {input_video}")
    print(f"Output: {output_video}")
    print(f"Text: '{text}'")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Branded video created: {output_video}")
        return output_video
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return None

def main():
    """Main function with argument parsing"""
    import argparse

    parser = argparse.ArgumentParser(description='Add branding to video')
    parser.add_argument('--input', default='brandingburner/social_izotx_Create_an_social_media-ted_image_with_realistic_lightin_dde068e9-edec-4a1e-b3bb-a03979919576_1.mp4', help='Input video path')
    parser.add_argument('--logo', default='brandingburner/logo.png', help='Logo PNG path')
    parser.add_argument('--text', default='Happy Maritime Day', help='Text to display')
    parser.add_argument('--output', default='brandingburner/final_branded_video.mp4', help='Output video path')

    args = parser.parse_args()

    # Validate input files
    if not os.path.exists(args.input):
        print(f"❌ Input video not found: {args.input}")
        sys.exit(1)

    if not os.path.exists(args.logo):
        print(f"❌ Logo not found: {args.logo}")
        sys.exit(1)

    # Add branding
    result = add_video_branding(args.input, args.logo, args.text, args.output)

    if result:
        size_mb = os.path.getsize(result) / (1024 * 1024)
        print(f"📊 Final video size: {size_mb:.1f} MB")
        print(f"🎉 Ready to use: {result}")
    else:
        print("❌ Failed to create branded video")
        sys.exit(1)

if __name__ == "__main__":
    main()
