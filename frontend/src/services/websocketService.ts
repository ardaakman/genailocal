// src/services/websocketService.ts

import { MemoryItem } from "../utils/models";

class WebSocketService {
  private socket: WebSocket | null = null;
  private messageHandlers: ((message: MemoryItem) => void)[] = [];

  connect(url: string): void {
    this.socket = new WebSocket(url);

    this.socket.onmessage = (event) => {
      const data: MemoryItem = JSON.parse(event.data);
      this.messageHandlers.forEach((handler) => handler(data));
    };

    this.socket.onclose = () => {
      console.log("WebSocket connection closed");
    };

    this.socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  }

  addMessageHandler(handler: (message: MemoryItem) => void): void {
    this.messageHandlers.push(handler);
  }

  removeMessageHandler(handler: (message: MemoryItem) => void): void {
    this.messageHandlers = this.messageHandlers.filter((h) => h !== handler);
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export const websocketService = new WebSocketService();
