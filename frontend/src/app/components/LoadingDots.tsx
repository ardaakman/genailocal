import React from "react";

interface LoadingDotsProps {
  label?: string;
}

const LoadingDots: React.FC<LoadingDotsProps> = ({ label }) => {
  return (
    <div className="flex flex-col items-center">
      <div className="flex items-center justify-center space-x-2">
        <div
          className="w-3 h-3 bg-gray-500 rounded-full animate-bounce"
          style={{ animationDelay: "0s" }}
        ></div>
        <div
          className="w-3 h-3 bg-gray-500 rounded-full animate-bounce"
          style={{ animationDelay: "0.2s" }}
        ></div>
        <div
          className="w-3 h-3 bg-gray-500 rounded-full animate-bounce"
          style={{ animationDelay: "0.4s" }}
        ></div>
      </div>
      {label && <p className="mt-2 text-sm text-gray-500">{label}</p>}
    </div>
  );
};

export default LoadingDots;
