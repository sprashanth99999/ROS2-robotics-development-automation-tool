import { create } from "zustand";

export interface GraphNode {
  id: string;
  label: string;
  type: "node" | "topic";
  data?: Record<string, unknown>;
}
export interface GraphEdge {
  source: string;
  target: string;
  type: "publishes" | "subscribes";
}
export interface TopicInfo {
  name: string;
  msg_type: string;
}

interface Ros2State {
  nodes: GraphNode[];
  edges: GraphEdge[];
  topics: TopicInfo[];
  loading: boolean;
  setGraph: (nodes: GraphNode[], edges: GraphEdge[]) => void;
  setTopics: (t: TopicInfo[]) => void;
  setLoading: (v: boolean) => void;
}

export const useRos2Store = create<Ros2State>((set) => ({
  nodes: [],
  edges: [],
  topics: [],
  loading: false,
  setGraph: (nodes, edges) => set({ nodes, edges }),
  setTopics: (topics) => set({ topics }),
  setLoading: (loading) => set({ loading }),
}));
