import React from "react";
import MemoryCard from "./MemoryCard";
import { MemoryItem } from "@/utils/models";

type MemoryListProps = {
  memories: MemoryItem[];
};

const MemoryList: React.FC<MemoryListProps> = ({ memories }) => (
  <div className="space-y-4">
    {memories.map((memory, index) => (
      <MemoryCard key={index} memory={memory} />
    ))}
  </div>
);

export default MemoryList;
