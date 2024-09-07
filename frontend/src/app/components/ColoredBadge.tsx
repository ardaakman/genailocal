import React, { useMemo } from "react";
import { Badge } from "@/components/ui/badge";

// Define a set of colors to use for badges
const badgeColors = [
  "bg-red-100 text-red-800",
  "bg-blue-100 text-blue-800",
  "bg-green-100 text-green-800",
  "bg-yellow-100 text-yellow-800",
  "bg-purple-100 text-purple-800",
  "bg-pink-100 text-pink-800",
  "bg-indigo-100 text-indigo-800",
  "bg-gray-100 text-gray-800",
];

// Function to consistently map a source to a color
const getColorForSource = (source: string): string => {
  const hash = source.split("").reduce((acc, char) => {
    return char.charCodeAt(0) + ((acc << 5) - acc);
  }, 0);
  return badgeColors[Math.abs(hash) % badgeColors.length];
};

interface ColoredBadgeProps {
  source: string;
  className?: string;
}

const ColoredBadge: React.FC<ColoredBadgeProps> = ({
  source,
  className = "",
}) => {
  const badgeColor = useMemo(() => getColorForSource(source), [source]);

  return (
    <Badge className={`font-semibold ${badgeColor} ${className}`}>
      {source}
    </Badge>
  );
};

export default ColoredBadge;
