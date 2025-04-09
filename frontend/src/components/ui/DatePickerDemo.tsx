"use client"

import * as React from "react"
import { format } from "date-fns" // Import format function to format date
import { Calendar as CalendarIcon } from "lucide-react" // Import Calendar Icon

import { cn } from "@/lib/utils" // Utility function to merge class names
import { Button } from "@/components/ui/button" // Custom Button component
import { Calendar } from "@/components/ui/calendar" // Custom Calendar component
import {
  Popover, // Popover component to display the calendar
  PopoverContent, // Content part of the popover where calendar is rendered
  PopoverTrigger, // The trigger that shows the calendar when clicked
} from "@/components/ui/popover"

export function DatePickerDemo() {
  // State to store the selected date
  const [date, setDate] = React.useState<Date>()

  return (
    <Popover>
      {/* Trigger button that opens the calendar */}
      <PopoverTrigger asChild>
        <Button
          variant={"outline"} // Style the button with outline
          className={cn(
            "w-[280px] justify-start text-left font-normal", // Button width and text alignment
            !date && "text-muted-foreground", // If no date is selected, apply muted text color
            "border-2 border-gray-800" // Apply a darker border outline
          )}
        >
          {/* Calendar Icon */}
          <CalendarIcon className="mr-2 h-4 w-4" />
          {/* Display selected date in 'PPP' format, or a default prompt */}
          {date ? format(date, "PPP") : <span>Pick a date</span>}
        </Button>
      </PopoverTrigger>

      {/* Content part of the popover, where the calendar is shown */}
      <PopoverContent className="w-auto p-0">
        {/* Calendar component with single mode (single date selection) */}
        <Calendar
          mode="single" // Allows selecting only one date
          selected={date} // Pass selected date as state
          onSelect={setDate} // Update state when a date is selected
          initialFocus // Focus on the calendar when it's opened
        />
      </PopoverContent>
    </Popover>
  )
}
