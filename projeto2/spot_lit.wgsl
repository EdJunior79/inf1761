struct Matrix {
  vertex: mat4x4<f32>,
  normal: mat4x4<f32>,
}
@group(1) @binding(0) var<storage, read> matrix: array<Matrix>;

struct Global {
  projection: mat4x4<f32>,
  light_ambient: vec3<f32>,
  light_diffuse: vec3<f32>,
  light_specular: vec3<f32>,
  light_position: vec4<f32>,
  camera_position: vec4<f32>,
  spot_direction: vec4<f32>,
  spot_cutoff: f32,
  spot_exponent: f32,
}
@group(0) @binding(0) var<uniform> global: Global;

struct Material {
  base_color: vec3<f32>,
  opacity: f32,
  specular_color: vec3<f32>,
  shininess: f32,
}
@group(2) @binding(0) var<uniform> material: Material;

struct VertexOutput {
  @builtin(position) clip_position: vec4<f32>,
  @location(0) normal: vec3<f32>,
  @location(1) light: vec3<f32>,
  @location(2) view: vec3<f32>,
}

@vertex
fn vs_main (@builtin(instance_index) instance_index: u32, @location(0) coord: vec3<f32>, @location(1) normal: vec3<f32>) -> VertexOutput {
  let m = matrix[instance_index];
  var out: VertexOutput;
  let veye = (m.vertex * vec4<f32>(coord, 1.0)).xyz;
  var light: vec3<f32>;
  if (global.light_position.w == 0.0) {
    light = normalize(global.light_position.xyz);
  } else {
    light = normalize(global.light_position.xyz - veye);
  }
  out.normal = (m.normal * vec4<f32>(normal, 0.0)).xyz;
  out.light = light;
  out.view = normalize(-veye);
  out.clip_position = global.projection * (m.vertex * vec4<f32>(coord, 1.0));
  return out;
}

@fragment
fn fs_main (in: VertexOutput) -> @location(0) vec4<f32> {
  let normal = normalize(in.normal);
  let light = normalize(in.light);
  let view = normalize(in.view);

  let c = dot(-light, normalize(global.spot_direction.xyz));

  var k_spot = 0.0;
  if (c >= global.spot_cutoff) {
    k_spot = pow(max(c, 0.0), global.spot_exponent);
  }

  var color = material.base_color * global.light_ambient.rgb;

  let ndotl = dot(normal, light);
  if (ndotl > 0.0 && k_spot > 0.0) {
    color += k_spot * material.base_color * global.light_diffuse.rgb * ndotl;
    let refl = normalize(reflect(-light, normal));
    color += k_spot * material.specular_color * global.light_specular.rgb * pow(max(0.0, dot(refl, view)), material.shininess);
  }
  return vec4<f32>(color, 1.0);
}