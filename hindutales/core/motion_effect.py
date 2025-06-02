import random
from enum import Enum
from typing import Tuple

class MotionEffect(Enum):
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    PAN_UP = "pan_up"
    PAN_DOWN = "pan_down"
    ZOOM_IN_PAN = "zoom_in_pan"
    ZOOM_OUT_PAN = "zoom_out_pan"
    SUBTLE_ZOOM = "subtle_zoom"

def get_motion_filter(effect: MotionEffect, duration: float, image_size: Tuple[int, int] = (1024, 1536)) -> str:
    """Generate ffmpeg filter string for various motion effects"""
    width, height = image_size
    
    if effect == MotionEffect.ZOOM_IN:
        return f"scale=2*{width}:2*{height},zoompan=z='min(zoom+0.0015,1.5)':d={int(duration*30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}"
    
    elif effect == MotionEffect.ZOOM_OUT:
        return f"scale=2*{width}:2*{height},zoompan=z='max(zoom-0.0015,1.0)':d={int(duration*30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}"
    
    elif effect == MotionEffect.PAN_LEFT:
        return f"scale=1.2*{width}:1.2*{height},zoompan=z=1:d={int(duration*30)}:x='iw-ow-(t/{duration})*(iw-ow)':y='ih/2-(ih/zoom/2)':s={width}x{height}"
    
    elif effect == MotionEffect.PAN_RIGHT:
        return f"scale=1.2*{width}:1.2*{height},zoompan=z=1:d={int(duration*30)}:x='(t/{duration})*(iw-ow)':y='ih/2-(ih/zoom/2)':s={width}x{height}"
    
    elif effect == MotionEffect.PAN_UP:
        return f"scale=1.2*{width}:1.2*{height},zoompan=z=1:d={int(duration*30)}:x='iw/2-(iw/zoom/2)':y='ih-oh-(t/{duration})*(ih-oh)':s={width}x{height}"
    
    elif effect == MotionEffect.PAN_DOWN:
        return f"scale=1.2*{width}:1.2*{height},zoompan=z=1:d={int(duration*30)}:x='iw/2-(iw/zoom/2)':y='(t/{duration})*(ih-oh)':s={width}x{height}"
    
    elif effect == MotionEffect.ZOOM_IN_PAN:
        # Zoom in while panning right
        return f"scale=2*{width}:2*{height},zoompan=z='min(zoom+0.001,1.3)':d={int(duration*30)}:x='(t/{duration})*(iw-ow)/2':y='ih/2-(ih/zoom/2)':s={width}x{height}"
    
    elif effect == MotionEffect.ZOOM_OUT_PAN:
        # Zoom out while panning left
        return f"scale=1.5*{width}:1.5*{height},zoompan=z='max(zoom-0.001,1.0)':d={int(duration*30)}:x='iw-ow-(t/{duration})*(iw-ow)/2':y='ih/2-(ih/zoom/2)':s={width}x{height}"
    
    elif effect == MotionEffect.SUBTLE_ZOOM:
        # Very subtle zoom for less dramatic effect
        return f"scale=1.1*{width}:1.1*{height},zoompan=z='1+0.05*sin(2*PI*t/{duration})':d={int(duration*30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}"
    
    else:
        # Default: slight zoom in
        return f"scale=1.1*{width}:1.1*{height},zoompan=z='min(zoom+0.0005,1.05)':d={int(duration*30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}"

def get_random_motion_effect() -> MotionEffect:
    """Get a random motion effect, weighted towards more subtle effects"""
    effects = [
        (MotionEffect.ZOOM_IN, 0.2),
        (MotionEffect.ZOOM_OUT, 0.2),
        (MotionEffect.PAN_LEFT, 0.15),
        (MotionEffect.PAN_RIGHT, 0.15),
        (MotionEffect.PAN_UP, 0.1),
        (MotionEffect.PAN_DOWN, 0.1),
        (MotionEffect.SUBTLE_ZOOM, 0.25),
        (MotionEffect.ZOOM_IN_PAN, 0.05),
        (MotionEffect.ZOOM_OUT_PAN, 0.05),
    ]
    
    effects_list, weights = zip(*effects)
    return random.choices(effects_list, weights=weights)[0]