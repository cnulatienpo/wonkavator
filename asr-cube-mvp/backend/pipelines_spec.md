# Pipelines (deterministic, no-AI ops)

## Image
- thumbnail(input) -> png
- palette_extract(input) -> palette.json
- montage(inputs[]) -> contact_sheet.pdf

## Audio
- split_cues(input.wav) -> /cues/*.wav + manifest.json
- normalize(input.wav) -> wav
- loop(input.wav, beats) -> wav

## Video
- keyframes(input.mp4) -> /frames/*.png
- scene_detect(input.mp4) -> edl.json
- grid(frames[]) -> png

## DICOM Echo
- extract_cycle(dcm) -> mp4_loop
- optical_flow(dcm) -> flow.mp4
- edge_trace(dcm) -> edges.svg
- audio_envelope(dcm) -> pulse.wav

## Texture Raster
- make_seamless(img) -> png
- derive_pbr(img) -> {albedo, normal, roughness, ao}
- readability_rig(maps) -> thumbs

Job graph: each oracle line expands to one or more steps; outputs are pinned back to cubelets.
