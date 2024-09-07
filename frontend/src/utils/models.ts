export type MemoryItem = {
  type: "memory" | "autocompletion" | "loading";
  source: string;
  summary: string;
  details: string;
  timestamp: Date;
};
