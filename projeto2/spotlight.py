import math
from typing import Any
import graphics_math as gm
from light import Light

class SpotLight(Light):
    """Fonte de luz do tipo spot com cone de abertura e decaimento angular."""

    def __init__(self,
                 x: float, y: float, z: float,
                 dx: float, dy: float, dz: float,
                 cutoff_angle: float, exponent: float = 10.0,
                 space: str = "world", **values: Any) -> None:
        super().__init__(space, **values)
        self.set_position(x, y, z)
        self.set_direction(dx, dy, dz)
        self.set_cutoff(cutoff_angle)
        self.set_exponent(exponent)

    def set_position(self, x: float, y: float, z: float) -> None:
        self.set("light_position", gm.vec4(x, y, z, 1.0))

    def set_direction(self, dx: float, dy: float, dz: float) -> None:
        d = gm.normalize(gm.vec3(dx, dy, dz))
        self.set("spot_direction", gm.vec4(d[0], d[1], d[2], 0.0))

    def set_cutoff(self, cutoff_angle_deg: float) -> None:
        self.set("spot_cutoff", math.cos(math.radians(cutoff_angle_deg)))

    def set_exponent(self, exponent: float) -> None:
        self.set("spot_exponent", float(exponent))

    def map(self, matrix: gm.Mat4) -> dict[str, Any]:
        position = self.get("light_position")
        direction = self.get("spot_direction")
        mapped_dir = matrix @ direction
        d = gm.normalize(gm.vec3(mapped_dir[0], mapped_dir[1], mapped_dir[2]))
        return {
            "light_position": matrix @ position,
            "spot_direction": gm.vec4(d[0], d[1], d[2], 0.0),
        }