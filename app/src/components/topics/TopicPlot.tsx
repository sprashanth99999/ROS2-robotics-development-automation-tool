import { useState, useEffect, useRef } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface Props {
  topicName: string;
  field?: string;
}

interface DataPoint {
  t: number;
  value: number;
}

export function TopicPlot({ topicName, field = "data" }: Props) {
  const [data, setData] = useState<DataPoint[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Subscribe via backend WS for topic data
    const ws = new WebSocket("ws://127.0.0.1:8765/ws");
    wsRef.current = ws;

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.type === `topic:${topicName}`) {
          setData((prev) => {
            const next = [...prev, { t: Date.now(), value: msg.payload?.[field] ?? 0 }];
            return next.slice(-100); // keep last 100 points
          });
        }
      } catch {}
    };

    return () => {
      ws.close();
    };
  }, [topicName, field]);

  return (
    <div style={{ padding: 12 }}>
      <div style={{ color: "#58a6ff", fontSize: 12, marginBottom: 8 }}>
        {topicName} — {field}
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <CartesianGrid stroke="#21262d" />
          <XAxis dataKey="t" tick={false} stroke="#30363d" />
          <YAxis stroke="#30363d" tick={{ fill: "#8b949e", fontSize: 10 }} />
          <Tooltip
            contentStyle={{ background: "#161b22", border: "1px solid #30363d", fontSize: 11 }}
            labelStyle={{ color: "#8b949e" }}
          />
          <Line type="monotone" dataKey="value" stroke="#3fb950" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
