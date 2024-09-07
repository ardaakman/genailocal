"use client";
import React, { useState, useEffect } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import Header from "../components/Header";
import Toast from "../components/Toast";
import MemoryList from "../components/MemoryList";
import { MemoryItem } from "../utils/models";
import LoadingDots from "../components/LoadingDots";
import { LightbulbIcon } from "lucide-react"; // Import the icon
import { cn } from "@/lib/utils";

const Memory: React.FC = () => {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [autoCompletion, setAutoCompletion] = useState<string>("");
  const [showToast, setShowToast] = useState(false);
  const { loading, data } = useWebSocket("ws://localhost:8080");

  useEffect(() => {
    if (data) {
      if (data.type === "memory") {
        setMemories((prev) => [
          ...prev,
          { ...data, timestamp: new Date() } as MemoryItem,
        ]);
        setShowToast(true);
        setTimeout(() => setShowToast(false), 3000);
      }

      if (data.type === "autocompletion") {
        setAutoCompletion(data.summary);
      }
    }
  }, [data]);

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Toast show={showToast} />
        <div className="bg-white shadow-md rounded-lg p-4 mb-6">
          <div className="flex items-center mb-2">
            <LightbulbIcon className="w-5 h-5 text-yellow-500 mr-2" />
            <h2 className="text-lg font-semibold text-gray-600">
              Autocomplete Suggestion
            </h2>
          </div>
          <p className={cn(autoCompletion ? "text-black" : "text-gray-400")}>
            {autoCompletion || "Nothing to show"}
          </p>
        </div>
        {loading && (
          <div className="flex justify-center items-center h-8">
            <LoadingDots />
          </div>
        )}
        <MemoryList memories={memories} />
      </main>
    </div>
  );
};

export default Memory;
