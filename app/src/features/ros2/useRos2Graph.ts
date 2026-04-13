import { useCallback } from "react";
import { useRos2Store } from "../../state/ros2Store";

const BACKEND = "http://127.0.0.1:8765";

export function useRos2Graph() {
  const { setGraph, setTopics, setLoading } = useRos2Store();

  const fetchGraph = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await fetch(`${BACKEND}/ros2/graph`);
      const data = await resp.json();
      setGraph(data.nodes || [], data.edges || []);
    } catch {
      setGraph([], []);
    } finally {
      setLoading(false);
    }
  }, [setGraph, setLoading]);

  const fetchTopics = useCallback(async () => {
    try {
      const resp = await fetch(`${BACKEND}/ros2/topics`);
      const data = await resp.json();
      setTopics(data || []);
    } catch {
      setTopics([]);
    }
  }, [setTopics]);

  const refresh = useCallback(async () => {
    await Promise.all([fetchGraph(), fetchTopics()]);
  }, [fetchGraph, fetchTopics]);

  return { fetchGraph, fetchTopics, refresh };
}
