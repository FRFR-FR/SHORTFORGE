# Anime Studio — FULLBODY2D

The previous LINEFORGE experiment used stroke-only Grease Pencil characters in a 3D environment. That did not match the intended art direction and is retired.

The active pipeline is **FULLBODY2D**: a fully 2D production stage containing complete, fully rendered people and props. Character volume comes from deliberate 2D draftsmanship — anatomy, construction, perspective, foreshortening, form shadows, cel shading, reflected light, material highlights, detailed clothing and layered hair. It must not look like stick figures, unshaded line drawings, flat icons or crude hinged cut-outs.

See the complete current guide:

- [FULLBODY2D production guide](fullbody2d/README.md)
- [Full-body character and prop renderer](fullbody2d/render.py)
- [Licensed anime reference downloader using yt-dlp](fullbody2d/download_references.py)
- [Reference source and licence register](fullbody2d/reference_sources.json)
- [Frame, motion and delivery QA](fullbody2d/qa.py)
- [GitHub Actions workflow](../.github/workflows/fullbody2d-anime.yml)

## Visual reference and rights

The first source is the Morevna Project, an independent open-source anime project. Its official site states that the Demo's visual parts and source files (excluding music) are CC BY 3.0; Morevna Episode 3 is CC BY-SA 4.0 and its animation sources are offered under the same licence. The workflow asks yt-dlp for video-only formats, checks the creator-published licence notice and stores references temporarily for study. Soundtracks are not downloaded. Reference footage is never inserted into the original episode or packaged in its release.

Sources:
- Morevna Demo: https://morevnaproject.org/anime/demo/
- Morevna Episode 3: https://morevnaproject.org/anime/episode-3/
- Morevna source library: https://morevnaproject.org/library/sources/
- Creative Commons BY 3.0: https://creativecommons.org/licenses/by/3.0/
- Creative Commons BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/

## Production status and quality bar

The six-second CI output is only a first procedural prototype proving the rendering pipeline and the full-body 2D design direction. It is not described as studio-quality anime. A production-ready episode needs expanded character turnarounds, several facial expressions, hand and footwear studies, costume and prop sheets, key poses, breakdowns, in-betweens, clean-up, compositing and a frame-by-frame human review.
