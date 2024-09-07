// src/hooks/useWebSocket.ts

import { useState, useEffect } from "react";
import { websocketService } from "../services/websocketService";
import { MemoryItem } from "../utils/models";

export const useWebSocket = (url: string) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<MemoryItem | null>(null);

  useEffect(() => {
    websocketService.connect(url);

    const handleMessage = (message: MemoryItem) => {
      if (message.type === "loading") {
        setLoading(true);
      } else {
        setLoading(false);
        setData(message);
      }
    };

    websocketService.addMessageHandler(handleMessage);

    return () => {
      websocketService.removeMessageHandler(handleMessage);
      websocketService.disconnect();
    };
  }, [url]);

  return { loading, data };
};
