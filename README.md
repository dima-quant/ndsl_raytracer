# ndsl_raytracer
NDSL Raytracer is a pure Python ray tracer implementation. Basically, it is a port of Trace of Radiance (https://github.com/mratsim/trace-of-radiance), rewritten in Python domain specific language (nimic) that transpiles to Nim.

<p style="text-align: center;">
  <img width="512" height="288" src="media/animation_rq.gif">
</p>

## Compile and run
For a single scene:
```
git clone https://github.com/dima-quant/ndsl_raytracer
cd ndsl_raytracer
uv sync
uv run -m nimic src/nraytracer/trace_of_radiance.py
cd src/nraytracer/ncache
nim c -d:danger --outdir:build trace_of_radiance.nim
./build/trace_of_radiance > image.ppm
```

For the animated scenes run the above with trace_of_radiance_animation.py and then convert the ppm images to mp4 with converter_ppm_to_mp4.py (convertion of mp4 to gif was made by Gifski app).
