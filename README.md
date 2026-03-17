# ndsl_raytracer
NDSL Raytracer is a pure Python ray tracer implementation. Basically, it is a port of Trace of Radiance (https://github.com/mratsim/trace-of-radiance), rewritten in Python domain specific language (nimic) that transpiles to Nim.

## Compile and run

```
git clone https://github.com/dima-quant/ndsl_raytracer
cd ndsl_raytracer
uv sync
uv run -m nimic src/nraytracer/trace_of_radiance.py
cd src/nraytracer/ncache
nim c -d:danger --outdir:build trace_of_radiance.nim
./build/trace_of_radiance > image.ppm
```