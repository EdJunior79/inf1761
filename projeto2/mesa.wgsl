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
  fog_color: vec4<f32>,
  fog_density: f32,
  clip_plane: vec4<f32>,
  clip_plane_color: vec4<f32>,
}
@group(0) @binding(0) var<uniform> global: Global;

struct Material {
  base_color: vec3<f32>,
  opacity: f32,
  specular_color: vec3<f32>,
  shininess: f32,
}
@group(2) @binding(0) var<uniform> material: Material;

@group(3) @binding(0) var decal_texture: texture_2d<f32>;
@group(3) @binding(1) var decal_sampler: sampler;

struct VertexOutput {
  @builtin(position) clip_position: vec4<f32>,
  @location(0) normal: vec3<f32>,
  @location(1) pos: vec3<f32>,
  @location(2) texcoord: vec2<f32>,
  @location(3) clip_dist: f32,
}

@vertex
fn vs_main (@builtin(instance_index) instance_index: u32, @location(0) coord: vec3<f32>,
            @location(1) normal: vec3<f32>, @location(2) texcoord: vec2<f32>) -> VertexOutput {
  let m = matrix[instance_index];
  let p = (m.vertex * vec4<f32>(coord, 1.0)).xyz;   // ponto no espaco do mundo
  var out: VertexOutput;
  out.normal = (m.normal * vec4<f32>(normal, 0.0)).xyz;
  out.pos = p;
  out.texcoord = texcoord;
  out.clip_dist = dot(global.clip_plane, vec4<f32>(p, 1.0));   // distancia ao plano de corte
  out.clip_position = global.projection * vec4<f32>(p, 1.0);
  return out;
}

@fragment
fn fs_main (in: VertexOutput, @builtin(front_facing) is_front: bool) -> @location(0) vec4<f32> {
  // amostra sempre, escolhe depois
  let decal = textureSample(decal_texture, decal_sampler, in.texcoord);

  // plano de corte
  if (in.clip_dist < 0.0) {
    discard;
  }

  let light = normalize(global.light_position.xyz - in.pos);
  let view = normalize(global.camera_position.xyz - in.pos);   // espaco do mundo: camera nao esta na origem

  // frente: objeto com textura; tras: tampa do corte
  var normal = normalize(in.normal);
  var base = material.base_color * decal.rgb;
  if (!is_front) {
    normal = -global.clip_plane.xyz;
    base = global.clip_plane_color.rgb;
  }

  // luz spot
  var k_spot = 0.0;
  let c = dot(-light, normalize(global.spot_direction.xyz));
  if (c >= global.spot_cutoff) {
    k_spot = pow(c, global.spot_exponent);
  }

  // Phong: a textura modula a parte fosca, o brilho e somado depois
  var color = base * global.light_ambient;
  let ndotl = dot(normal, light);
  if (ndotl > 0.0) {
    color += k_spot * base * global.light_diffuse * ndotl;
    let refl = normalize(reflect(-light, normal));
    color += k_spot * material.specular_color * global.light_specular * pow(max(0.0, dot(refl, view)), material.shininess);
  }

  // fog exponencial quadratico
  let s = length(global.camera_position.xyz - in.pos);
  let f = exp(-pow(global.fog_density * s, 2.0));
  color = f * color + (1.0 - f) * global.fog_color.rgb;

  return vec4<f32>(color, 1.0);
}
