import React from "react";

interface SummaryProps {
  graphData: { 
    data1: { month: string; visitors: number }[]; 
    data2: { month: string; visitors: number }[] 
  };
}

const Summary: React.FC<SummaryProps> = ({ graphData }) => {
  return (
    <div className="w-full flex flex-col items-center ">
    

      {/* Centered Textarea with 70% Width */}
      <textarea
        className="w-[70%] h-24 p-3 text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg resize-none"
        placeholder="Detailed analysis will be generated here..."
        readOnly
      />
    </div>
  );
};

export default Summary;
