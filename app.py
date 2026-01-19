import os
import ffmpeg


def trim(in_file: str, out_file: str, start: int, end: int) -> None:
    if os.path.exists(out_file):
        os.remove(out_file)

    probe_result = ffmpeg.probe(in_file)
    in_file_duration = probe_result.get("format", {}).get("duration", None)
    print(in_file_duration)

    input_stream = ffmpeg.input(in_file)

    pts = "PTS-STARTPTS"
    video = input_stream.trim(start=start, end=end).setpts(pts)
    audio = input_stream.filter_("atrim", start=start, end=end).filter_("asetpts", pts)
    video_and_audio = ffmpeg.concat(video, audio, v=1, a=1)
    output = ffmpeg.output(video_and_audio, out_file, format="mp4")
    output.run()


trim(in_file="movie.mp4", out_file="out.mp4", start=210, end=238)
