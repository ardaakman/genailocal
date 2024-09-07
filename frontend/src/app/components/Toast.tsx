import React from "react";
import { AlertCircle } from "lucide-react";

type ToastProps = {
  show: boolean;
};

const Toast: React.FC<ToastProps> = ({ show }) => {
  if (!show) return null;

  return (
    <div className="fixed top-4 right-4 z-50 animate-in fade-in slide-in-from-top-5 duration-300">
      <div className="bg-black text-white px-4 py-3 rounded-lg shadow-lg flex items-center space-x-2">
        <AlertCircle className="h-5 w-5" />
        <p className="font-medium">Memory updated</p>
      </div>
    </div>
  );
};

export default Toast;
