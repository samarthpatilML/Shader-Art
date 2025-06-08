#vertex
#version 330

in vec3 in_position;

uniform mat4 model;
uniform mat4 view;
uniform mat4 proj;

out vec3 v_position;

void main() {
    v_position = in_position;
    gl_Position = proj * view * model * vec4(in_position, 1.0);
    gl_PointSize = 5.0;
}

#fragment
#version 330

in vec3 v_position;

out vec4 fragColor;

void main() {
    // Make points circular and smooth edges
    float dist = length(gl_PointCoord - vec2(0.5));
    if (dist > 0.5) {
        discard;
    }

    // Color based on position, remap to 0..1
    vec3 color = 0.5 + 0.5 * normalize(v_position);

    // Add glow effect with smooth alpha
    float alpha = smoothstep(0.5, 0.4, dist);

    fragColor = vec4(color, alpha);
}
