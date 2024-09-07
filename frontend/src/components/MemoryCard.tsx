import React, { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Separator } from "../components/ui/separator";
import { MemoryItem } from "../utils/models";
import ColoredBadge from "./ColoredBadge"; // Make sure to import from the correct path

type MemoryCardProps = {
  memory: MemoryItem;
};

const MemoryCard: React.FC<MemoryCardProps> = ({ memory }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card className="w-full hover:shadow-md transition-shadow duration-300">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div>
          <ColoredBadge source={memory.source} />
        </div>
        <CardTitle className="text-sm font-medium text-gray-500">
          {memory.timestamp.toLocaleTimeString()}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-700 leading-relaxed">
          {memory.summary}
        </p>
        <div className="mt-4 flex justify-end">
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-blue-500 hover:text-blue-700 focus:outline-none transition-colors duration-200"
          >
            {expanded ? (
              <span className="flex items-center">
                Hide Details
                <ChevronUp className="ml-1 h-3 w-3" />
              </span>
            ) : (
              <span className="flex items-center">
                View Details
                <ChevronDown className="ml-1 h-3 w-3" />
              </span>
            )}
          </button>
        </div>
      </CardContent>
      {expanded && (
        <>
          <Separator className="my-2" />
          <CardContent>
            <p className="text-sm text-gray-600 mt-2 leading-relaxed">
              {memory.details}
            </p>
          </CardContent>
        </>
      )}
    </Card>
  );
};

export default MemoryCard;
