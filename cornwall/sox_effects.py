"""Build SoX effect arguments from Cornwall effects chains.

Shared between play.py and fx.py so the logic isn't duplicated.
"""

from cornwall import state


def build_sox_effects(track_id: int) -> list[str]:
    """Build SoX command-line effect arguments from a track's effects chain."""
    effects = state.get_track_effects(track_id)
    args = []
    for fx in effects:
        name = fx["name"]
        params = fx.get("params", {})

        if name == "reverb":
            args.append("reverb")
            if "reverberance" in params:
                args.append(str(params["reverberance"]))
            if "hf_damping" in params:
                args.append(str(params["hf_damping"]))
            if "room_scale" in params:
                args.append(str(params["room_scale"]))
        elif name == "delay":
            args.append("echo")
            args.append(str(params.get("gain_in", 0.8)))
            args.append(str(params.get("gain_out", 0.9)))
            args.append(str(params.get("delay_ms", 500)))
            args.append(str(params.get("decay", 0.3)))
        elif name == "chorus":
            args.append("chorus")
            args.append(str(params.get("gain_in", 0.7)))
            args.append(str(params.get("gain_out", 0.9)))
            args.append(str(params.get("delay_ms", 55)))
            args.append(str(params.get("decay", 0.4)))
            args.append(str(params.get("speed", 0.25)))
            args.append("-" + str(params.get("shape", "s")))
        elif name == "flanger":
            args.append("flanger")
        elif name == "phaser":
            args.append("phaser")
        elif name == "tremolo":
            args.append("tremolo")
            args.append(str(params.get("speed", 6)))
            if "depth" in params:
                args.append(str(params["depth"]))
        elif name == "overdrive":
            args.append("overdrive")
            args.append(str(params.get("gain", 20)))
        elif name == "compressor":
            args.append("compand")
            args.append(str(params.get("attack_decay", "0.3,1")))
            args.append(str(params.get("transfer", "6:-70,-60,-20")))
        elif name == "eq":
            args.append("equalizer")
            args.append(str(params.get("frequency", 1000)))
            args.append(str(params.get("width", "1q")))
            args.append(str(params.get("gain", 0)))
        elif name == "bass":
            args.append("bass")
            args.append(str(params.get("gain", 0)))
        elif name == "treble":
            args.append("treble")
            args.append(str(params.get("gain", 0)))
        elif name == "lowpass":
            args.append("lowpass")
            args.append(str(params.get("frequency", 3000)))
        elif name == "highpass":
            args.append("highpass")
            args.append(str(params.get("frequency", 300)))
        elif name == "pitch":
            args.append("pitch")
            args.append(str(params.get("cents", 0)))
        elif name == "tempo":
            args.append("tempo")
            args.append(str(params.get("factor", 1.0)))
        elif name == "norm":
            args.append("norm")
            if "level" in params:
                args.append(str(params["level"]))
        elif name == "fade":
            args.append("fade")
            args.append(str(params.get("type", "t")))
            args.append(str(params.get("fade_in", 0)))
            args.append(str(params.get("stop", 0)))
            args.append(str(params.get("fade_out", 0)))
        elif name == "lowpass":
            args.append("lowpass")
            args.append(str(params.get("frequency", 3000)))
        elif name == "highpass":
            args.append("highpass")
            args.append(str(params.get("frequency", 300)))
        else:
            # Pass through as raw sox effect
            args.append(name)
            for v in params.values():
                args.append(str(v))

    return args
