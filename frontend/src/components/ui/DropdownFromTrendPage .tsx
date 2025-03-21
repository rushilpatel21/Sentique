import React, { useState } from "react";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button"; // Using ShadCN button for a clean UI
import { ChevronDownIcon } from "lucide-react";

const dropdownValues = [
  "Performance",
  "Security",
  "User Interface",
  "Pricing",
  "Customer Support",
  "Driver Experience",
  "App Reliability",
  "Ride Availability",
  "Payment and Transactions",
  "Regulations and Legal",
  "Company Policies",
  "Sustainability and Environment",
  "Rider Experience",
  "Vehicle Quality",
  "Community Impact",
  "Marketing and Communication",
];

// Accepts an `onChange` prop to notify the parent component when the selection changes
interface DropdownProps {
  onChange?: (selected: string) => void;
}

const DropdownFromTrendPage: React.FC<DropdownProps> = ({ onChange }) => {
  const [selectedOption, setSelectedOption] = useState<string>("");

  const handleSelect = (option: string) => {
    setSelectedOption(option);
    if (onChange) {
      onChange(option); // Notify the parent component
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="flex items-center justify-between w-56 px-4 py-2">
          {selectedOption || "Select Category"}
          <ChevronDownIcon className="ml-2 h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56 mt-2 shadow-md rounded-md">
        <DropdownMenuLabel className="px-3 py-2 text-sm font-semibold text-gray-700">
          Choose Category
        </DropdownMenuLabel>
        <div className="max-h-60 overflow-y-auto">
          {dropdownValues.map((option) => (
            <DropdownMenuItem
              key={option}
              className="cursor-pointer px-3 py-2 hover:bg-gray-100"
              onSelect={() => handleSelect(option)}
            >
              {option}
            </DropdownMenuItem>
          ))}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default DropdownFromTrendPage;
