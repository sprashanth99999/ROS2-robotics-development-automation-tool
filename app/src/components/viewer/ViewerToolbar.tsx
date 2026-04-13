interface Props {
  onReset?: () => void;
  onToggleGrid?: () => void;
  onToggleAxes?: () => void;
}

export function ViewerToolbar({ onReset, onToggleGrid, onToggleAxes }: Props) {
  const btn = {
    background: "#21262d", color: "#c9d1d9", border: "1px solid #30363d",
    borderRadius: 4, padding: "4px 10px", cursor: "pointer", fontSize: 11,
  };

  return (
    <div style={{ padding: "6px 12px", borderBottom: "1px solid #21262d", display: "flex", gap: 6 }}>
      <b style={{ color: "#58a6ff", fontSize: 13, marginRight: 8 }}>3D Viewer</b>
      {onReset && <button style={btn} onClick={onReset}>Reset View</button>}
      {onToggleGrid && <button style={btn} onClick={onToggleGrid}>Grid</button>}
      {onToggleAxes && <button style={btn} onClick={onToggleAxes}>Axes</button>}
    </div>
  );
}
