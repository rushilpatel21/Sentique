import { TrendingUp } from "lucide-react"; // Import TrendingUp icon
import ButtonGroup from "../components/ui/ButtonGroup"; // Import ButtonGroup component
import BarChartComponent from "../components/ui/barChart"; // Import the chart component (corrected casing)
import { LineChartComponent } from "../components/ui/lineChart"; // Import the LineChart component

export function Home() {
  return (
    <div>
      {/* ButtonGroup component without any operations */}
      <ButtonGroup defaultSelected="DEFAULT" onSelectionChange={() => { }} />

      <div className="mt-6 grid grid-cols-2 gap-3">
        {/* Display both charts side by side */}
        <BarChartComponent />
        <LineChartComponent />
      </div>
    </div>

  );
}
