// src/hooks/useWebSocket.ts

import { useState, useEffect } from "react";
import { websocketService } from "../services/websocketService";

type WebSocketMessage = {
  source?: string;
  summary?: string;
  details?: string;
  token?: string;
};

export const useWebSocket = (url: string) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<WebSocketMessage | null>(null);

  useEffect(() => {
    websocketService.connect(url);

    const handleMessage = (message: WebSocketMessage) => {
      if ("token" in message) {
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
