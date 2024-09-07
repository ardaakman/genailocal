"use client";
import React, { useState, useEffect } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import Header from "./components/Header";
import Toast from "./components/Toast";
import MemoryList from "./components/MemoryList";
import { MemoryItem } from "@/utils/models";
import LoadingDots from "./components/LoadingDots";

const Memory: React.FC = () => {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [showToast, setShowToast] = useState(false);
  const { loading, data } = useWebSocket("ws://localhost:8080");

  useEffect(() => {
    if (data && "source" in data) {
      setMemories((prev) => [
        ...prev,
        { ...data, timestamp: new Date() } as MemoryItem,
      ]);
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
    }
  }, [data]);

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Toast show={showToast} />
        {loading && (
          <div className="flex justify-center items-center h-24">
            <LoadingDots />
          </div>
        )}
        <MemoryList memories={memories} />
      </main>
    </div>
  );
};

export default Memory;
