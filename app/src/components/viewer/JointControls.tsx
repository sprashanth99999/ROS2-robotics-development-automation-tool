interface JointDef {
  name: string;
  type: string;
  lower: number;
  upper: number;
  value: number;
}

interface Props {
  joints: JointDef[];
  onChange: (name: string, value: number) => void;
}

export function JointControls({ joints, onChange }: Props) {
  const movable = joints.filter((j) => j.type !== "fixed");

  if (movable.length === 0) {
    return (
      <div style={{ padding: 12, color: "#8b949e", fontSize: 12 }}>
        No movable joints
      </div>
    );
  }

  return (
    <div style={{ padding: 12, maxHeight: 300, overflow: "auto" }}>
      <b style={{ color: "#58a6ff", fontSize: 12, display: "block", marginBottom: 8 }}>
        Joints
      </b>
      {movable.map((j) => (
        <div key={j.name} style={{ marginBottom: 8 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#c9d1d9" }}>
            <span>{j.name}</span>
            <span style={{ color: "#8b949e" }}>{j.value.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min={j.lower}
            max={j.upper}
            step={0.01}
            value={j.value}
            onChange={(e) => onChange(j.name, parseFloat(e.target.value))}
            style={{ width: "100%", accentColor: "#238636" }}
          />
        </div>
      ))}
    </div>
  );
}
