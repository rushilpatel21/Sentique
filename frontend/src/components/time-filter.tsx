"use client"

import { Button } from "@/components/ui/button";

// Define the props interface
interface TimeFilterProps {
  setTimeFilter: (time: string) => void;
}

export function TimeFilter({ setTimeFilter }: TimeFilterProps) {
  const handleTimeFilterChange = (time: string) => {
    setTimeFilter(time);
  };

  return (
    <div className="flex space-x-2">
      <Button
        variant="outline"
        size="sm"
        className="h-8"
        onClick={() => handleTimeFilterChange("default")}
      >
        DEFAULT
      </Button>
      <Button
        variant="outline"
        size="sm"
        className="h-8"
        onClick={() => handleTimeFilterChange("7d")}
      >
        7D
      </Button>
      <Button
        variant="outline"
        size="sm"
        className="h-8"
        onClick={() => handleTimeFilterChange("14d")}
      >
        14D
      </Button>
      <Button
        variant="outline"
        size="sm"
        className="h-8"
        onClick={() => handleTimeFilterChange("4w")}
      >
        4W
      </Button>
      <Button
        variant="outline"
        size="sm"
        className="h-8"
        onClick={() => handleTimeFilterChange("3m")}
      >
        3M
      </Button>
      <Button
        variant="outline"
        size="sm"
        className="h-8"
        onClick={() => handleTimeFilterChange("6m")}
      >
        6M
      </Button>
      <Button
        variant="outline"
        size="sm"
        className="h-8"
        onClick={() => handleTimeFilterChange("12m")}
      >
        12M
      </Button>
      <Button
        variant="outline"
        size="sm"
        className="h-8"
        onClick={() => handleTimeFilterChange("custom")}
      >
        CUSTOM
      </Button>
    </div>
  );
}