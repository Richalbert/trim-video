# Amelioration de Claude
import os
import ffmpeg
from typing import Optional


def trim(
    in_file: str,
    out_video: str,
    out_audio: str,
    start: float,
    end: float,
    overwrite: bool = True,
    verbose: bool = False,
) -> None:
    """
    Découpe une vidéo entre deux timestamps.

    Args:
        in_file: Chemin du fichier vidéo source
        out_video: Chemin du fichier de sortie pour la video
        out_audio: Chemin du fichier de sortie pour l'audio
        start: Temps de début en secondes
        end: Temps de fin en secondes
        overwrite: Si True, écrase le fichier de sortie s'il existe
        verbose: Si True, affiche des informations de debug

    Raises:
        FileNotFoundError: Si le fichier d'entrée n'existe pas
        ValueError: Si les timestamps sont invalides
    """
    # Vérifications
    if not os.path.exists(in_file):
        raise FileNotFoundError(f"Le fichier {in_file} n'existe pas")

    if start < 0 or end < 0:
        raise ValueError("Les timestamps doivent être positifs")

    if start >= end:
        raise ValueError(
            "Le timestamp de début doit être inférieur au timestamp de fin"
        )

    # Récupère la durée de la vidéo
    try:
        probe_result = ffmpeg.probe(in_file)
        duration = float(probe_result.get("format", {}).get("duration", 0))

        if verbose:
            print(f"Durée de la vidéo : {duration:.2f}s")

        if end > duration:
            raise ValueError(
                f"Le timestamp de fin ({end}s) dépasse la durée de la vidéo ({duration:.2f}s)"
            )

    except ffmpeg.Error as e:
        raise RuntimeError(f"Erreur lors de l'analyse du fichier : {e.stderr.decode()}")

    # Gestion du fichier de sortie video
    if os.path.exists(out_video):
        if overwrite:
            os.remove(out_video)
            if verbose:
                print(f"Fichier {out_video} existant supprimé")
        else:
            raise FileExistsError(f"Le fichier {out_video} existe déjà")

    # Gestion du fichier de sortie audio
    if os.path.exists(out_audio):
        if overwrite:
            os.remove(out_audio)
            if verbose:
                print(f"Fichier {out_audio} existant supprimé")
        else:
            raise FileExistsError(f"Le fichier {out_audio} existe déjà")

    # Traitement
    try:
        input_stream = ffmpeg.input(in_file)

        pts = "PTS-STARTPTS"
        video = input_stream.trim(start=start, end=end).setpts(pts)
        audio = input_stream.filter_("atrim", start=start, end=end).filter_(
            "asetpts", pts
        )

        # Traitement de la video
        output_video = ffmpeg.output(video, audio, out_video, format="mp4")
        output_video.run(capture_stdout=not verbose, capture_stderr=not verbose)

        # Traitement de l'audio
        output_audio = ffmpeg.output(audio, out_audio, format="mp3")
        output_audio.run(capture_stdout=not verbose, capture_stderr=not verbose)

        if verbose:
            print(f"✓ Vidéo découpée avec succès : {out_video}")
            print(f"✓ Audio extrait avec succès : {out_audio}")
            print(f"  Segment extrait : {start}s → {end}s ({end - start}s)")

    except ffmpeg.Error as e:
        raise RuntimeError(f"Erreur FFmpeg : {e.stderr.decode()}")


if __name__ == "__main__":
    # Exemple d'utilisation
    try:
        trim(
            in_file="movie.mp4",
            out_video="out.mp4",
            out_audio="out.mp3",
            start=16,
            end=116,
            verbose=True,
        )
    except Exception as e:
        print(f"Erreur : {e}")
