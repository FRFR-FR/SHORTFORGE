# Anime Studio — FULLBODY2D

The previous LINEFORGE experiment used stroke-only characters in a 3D environment. That did not match the requested art direction and is retired.

The active pipeline is **FULLBODY2D**: a fully 2D production stage containing complete, fully rendered people and designed props. Their three-dimensional appearance must come from the artwork itself: anatomy, form construction, foreshortening, layered shapes, perspective, cel shadows, reflected light, material highlights, clothing construction, hair design and detailed cleanup.

## Current files

- [FULLBODY2D production guide](fullbody2d/README.md)
- [Full-body character and prop renderer](fullbody2d/render.py)
- [yt-dlp licensed anime reference downloader](fullbody2d/download_references.py)
- [Reference palette and contrast analysis](fullbody2d/analyze_reference.py)
- [Reference source and licence register](fullbody2d/reference_sources.json)
- [Frame, motion and delivery QA](fullbody2d/qa.py)
- [GitHub Actions workflow](../.github/workflows/fullbody2d-anime.yml)

## Downloaded anime references

The pipeline uses yt-dlp to download direct, openly licensed files from Wikimedia Commons. Its primary reference is **Morevna Episode 3.0.2**, a futuristic anime episode by Morevna Project. A second reference, **Pepper & Carrot Motion Comic — Episode 6**, is used for 2D illustrated character and prop design.

The job checks the source-file SHA-1 hashes, strips muxed soundtrack audio into video-only files, deletes the original temporary downloads, and samples contact sheets. A numeric palette/contrast guide feeds the original scene renderer. No source video, artwork, frame or soundtrack appears in the final video.

The licences and attribution are recorded in [the FULLBODY2D guide](fullbody2d/README.md) and [reference register](fullbody2d/reference_sources.json). Morevna Episode 3's creator description says CC BY-SA 4.0 while its current Commons file page lists CC BY 4.0; the project conservatively follows the creator-stated CC BY-SA 4.0 terms. Pepper & Carrot Episode 6 is CC BY-SA 4.0, with a Commons VRT permission record.

## Quality status

The current six-second CI test is a procedural prototype to validate 2D composition, two complete character designs, material shading, props, frame motion and the reference palette workflow. It is not a claim of studio-quality anime. Long-form production requires detailed turnarounds, expression sheets, hand studies, pose design, breakdowns, in-betweens, cleanup and visual supervision.

## References

- https://commons.wikimedia.org/wiki/File:Morevna_Episode_3.0.2_(English).webm
- https://commons.wikimedia.org/wiki/File:Morevna_Project_-_Pepper%26Carrot_(animated_comic)_-_Episode_6_-_The_Potion_Contest.webm
- https://morevnaproject.org/anime/episode-3/
- https://morevnaproject.org/pepper-and-carrot/episode-6/
