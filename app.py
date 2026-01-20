# Amelioration de Claude
import os
import ffmpeg
from typing import Optional


def trim(
    in_file: str,
    out_file: str,
    start: float,
    end: float,
    overwrite: bool = True,
    verbose: bool = False,
) -> None:
    """
    Découpe une vidéo entre deux timestamps.

    Args:
        in_file: Chemin du fichier vidéo source
        out_file: Chemin du fichier de sortie
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

    # Gestion du fichier de sortie
    if os.path.exists(out_file):
        if overwrite:
            os.remove(out_file)
            if verbose:
                print(f"Fichier {out_file} existant supprimé")
        else:
            raise FileExistsError(f"Le fichier {out_file} existe déjà")

    # Traitement
    try:
        input_stream = ffmpeg.input(in_file)

        pts = "PTS-STARTPTS"
        video = input_stream.trim(start=start, end=end).setpts(pts)
        audio = input_stream.filter_("atrim", start=start, end=end).filter_(
            "asetpts", pts
        )

        # Pas besoin de concat, on passe directement video et audio
        output = ffmpeg.output(video, audio, out_file, format="mp4")
        output.run(capture_stdout=not verbose, capture_stderr=not verbose)

        if verbose:
            print(f"✓ Vidéo découpée avec succès : {out_file}")
            print(f"  Segment extrait : {start}s → {end}s ({end - start}s)")

    except ffmpeg.Error as e:
        raise RuntimeError(f"Erreur FFmpeg : {e.stderr.decode()}")


if __name__ == "__main__":
    # Exemple d'utilisation
    try:
        trim(in_file="movie.mp4", out_file="out.mp4", start=536, end=629, verbose=True)
    except Exception as e:
        print(f"Erreur : {e}")
