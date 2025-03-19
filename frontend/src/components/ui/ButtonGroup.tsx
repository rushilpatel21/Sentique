import { Calendar1Icon } from "lucide-react"; // Import Calendar icon from lucide-react
import React, { useState, useRef } from "react"; // Import React and hooks

import { DatePickerDemo } from "./DatePickerDemo"; // Import the DatePickerDemo component to show calendar on CUSTOM selection

// ButtonGroupProps interface defines the expected props for the ButtonGroup component
interface ButtonGroupProps {
  defaultSelected: string; // Default value for the selected button
  onSelectionChange: (selectedValue: string) => void; // Callback to handle button selection changes
}

const ButtonGroup: React.FC<ButtonGroupProps> = ({ defaultSelected, onSelectionChange }) => {
  // State to keep track of the currently selected button value
  const [selected, setSelected] = useState<string>(defaultSelected);

  // State to manage if the "CUSTOM" option is selected and calendar should be shown
  const [isCustomSelected, setIsCustomSelected] = useState<boolean>(false);

  // Ref to the "CUSTOM" button for positioning purposes if needed
  const customButtonRef = useRef<HTMLButtonElement | null>(null);

  // Handle button click, updates the selected state and triggers the callback
  const handleButtonClick = (value: string) => {
    setSelected(value);
    onSelectionChange(value);
    // If "CUSTOM" is selected, display the calendar; otherwise, hide it
    if (value === "CUSTOM") {
      setIsCustomSelected(true);
    } else {
      setIsCustomSelected(false);
    }
  };

  // Options for the buttons (default selections plus "CUSTOM")
  const options = [
    { label: "DEFAULT", value: "DEFAULT" },
    { label: "7D", value: "7D" },
    { label: "14D", value: "14D" },
    { label: "4W", value: "4W" },
    { label: "3M", value: "3M" },
    { label: "6M", value: "6M" },
    { label: "12M", value: "12M" },
    { label: "CUSTOM", value: "CUSTOM" }, // Custom option to show the calendar
  ];

  return (
    <div className="flex gap-2 p-2 bg-gray-100 rounded-lg shadow-md relative">
      {/* Calendar Icon */}
      <span className="flex items-center">
        <Calendar1Icon />
      </span>

      {/* Map through the options and render buttons */}
      {options.map((option) => (
        <button
          key={option.value} // Key to uniquely identify each button
          ref={option.value === "CUSTOM" ? customButtonRef : null} // Reference to the custom button if needed
          className={`px-4 py-2 text-sm font-medium uppercase rounded-md transition duration-300 
            ${selected === option.value ? "bg-blue-500 text-white border-blue-500" : "bg-white text-gray-700 border-transparent hover:bg-gray-200"} 
            border border-solid focus:outline-none`}
          onClick={() => handleButtonClick(option.value)} // Handle button click
        >
          {option.label} {/* Display button label */}
        </button>
      ))}

      {/* Conditionally render DatePickerDemo component when "CUSTOM" is selected */}
      {isCustomSelected && <DatePickerDemo />}
    </div>
  );
};

export default ButtonGroup;
