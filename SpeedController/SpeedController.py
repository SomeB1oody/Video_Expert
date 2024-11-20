import subprocess
import os

def change_video_speed(video_path, output_path, speed, keep_pitch):
    try:
        # Ensure speed is a valid float
        speed = float(speed)
        if speed <= 0:
            raise ValueError("Speed must be greater than 0.")

        # Handle audio speed exceeding the atempo limit
        atempo_filters = []
        while speed > 2.0:
            atempo_filters.append("atempo=2.0")
            speed /= 2.0
        atempo_filters.append(f"atempo={speed}")
        atempo_filter = ",".join(atempo_filters)

        if keep_pitch.lower() == 'y':
            # Apply speed change while preserving audio pitch
            cmd = [
                "ffmpeg", "-i", video_path, "-filter_complex",
                f"[0:v]setpts={1/speed}*PTS[v];[0:a]{atempo_filter}[a]",
                "-map", "[v]", "-map", "[a]", output_path
            ]
        else:
            # Apply speed change without preserving audio pitch
            cmd = [
                "ffmpeg", "-i", video_path, "-filter_complex",
                f"[0:v]setpts={1/speed}*PTS[v];[0:a]{atempo_filter}[a]",
                "-map", "[v]", "-map", "[a]", output_path
            ]

        # Execute the FFmpeg command
        subprocess.run(cmd, check=True)
    except ValueError as ve:
        raise ValueError(ve)
    except subprocess.CalledProcessError as e:
        raise ValueError(e)

if __name__ == "__main__":
    # 询问用户输入
    video_path = input("Please enter input path ").strip()

    try:
        speed = float(input("Please enter speed (bigger than 0): "))
        if speed <= 0:
            raise ValueError("speed must bigger than 0!")
    except ValueError as e:
        print(e)
        exit(1)

    keep_pitch = input("Do you maintain tone? (y/n): ").strip().lower()
    if keep_pitch not in ['y', 'n']:
        print("Please enter 'y' or 'n'!")
        exit(1)

    output_path = input("Please enter the full path of the output file (including file name and extension) : ").strip()
    if not output_path:
        print("The output path cannot be empty! ")
        exit(1)

    try:
        change_video_speed(video_path, output_path, speed, keep_pitch)
    except Exception as e:
        print(e)
