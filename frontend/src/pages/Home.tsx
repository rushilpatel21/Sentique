import ButtonGroup from "../components/ui/ButtonGroup";
import BarChartComponent from "../components/ui/barChart";
import { LineChartComponent } from "../components/ui/lineChart";
import CustomBarChartComponent from "@/components/ui/CustomBarChart";

// Dynamic data for the first Bar Chart
const chartData1 = [
  { browser: "chrome", visitors: 275, fill: "var(--color-chrome)" },
  { browser: "safari", visitors: 200, fill: "var(--color-safari)" },
  { browser: "firefox", visitors: 187, fill: "var(--color-firefox)" },
  { browser: "edge", visitors: 173, fill: "var(--color-edge)" },
  { browser: "other", visitors: 90, fill: "var(--color-other)" },
];

const chartConfig1 = {
  visitors: { label: "Visitors" },
  chrome: { label: "Playstore", color: "hsl(var(--chart-1))" },
  safari: { label: "Reddit", color: "hsl(var(--chart-2))" },
  firefox: { label: "X", color: "hsl(var(--chart-3))" },
  edge: { label: "AppStore", color: "hsl(var(--chart-4))" },
  other: { label: "Trust Pilot", color: "hsl(var(--chart-5))" },
};

const complaintsData = [
  { reason: "Issue With Audio Connection", count: 1400, fill: "#007bff" },
  { reason: "Issue With Sound Quality", count: 721, fill: "#28a745" },
  { reason: "Issue With Meetings Disconnecting", count: 598, fill: "#dc3545" },
  { reason: "Issue With Video Lag in Zoom", count: 583, fill: "#fd7e14" },
  { reason: "Issue With Video Not Working", count: 577, fill: "#d63384" },

];


const improvementsData = [
  { reason: "Suggest To Address Sound Issues", count: 72, fill: "#007bff" },
  { reason: "Ability To Have Arabic Version", count: 27, fill: "#28a745" },
  { reason: "Improve Audio Quality", count: 21, fill: "#dc3545" },
  { reason: "Ability To Improve Zoom App", count: 20, fill: "#fd7e14" },
  { reason: "Improvement In Ease of Use", count: 19, fill: "#d63384" },

];


const praisesData = [
  { reason: "Happy With Zoom For Meetings", count: 6900, fill: "#007bff" },
  { reason: "Happy With The User-Friendly UI", count: 824, fill: "#28a745" },
  { reason: "Happy With Audio Quality", count: 283, fill: "#dc3545" },
  { reason: "Happy With Zoom For Classes", count: 229, fill: "#fd7e14" },
  { reason: "Happy With Good Video Quality", count: 180, fill: "#d63384" },
  { reason: "Happy With Zoom For Education", count: 179, fill: "#6610f2" },

];


// We'll use the same configuration for simplicity,
// but you could also pass different configurations if needed.
const chartConfigCommon = chartConfig1;

export function Home() {
  return (
    <div>
      {/* ButtonGroup component without any operations */}
      <ButtonGroup defaultSelected="DEFAULT" onSelectionChange={() => { }} />

      <div className="mt-6 grid grid-cols-2 gap-4">
        {/* Multiple BarChartComponents with different data */}
        <BarChartComponent
          title="Sources of Feedback"
          description="January - June 2024"
          data={chartData1}
          config={chartConfigCommon}

        />

        <LineChartComponent />
      </div>


      <div className="mt-6 grid grid-cols-3 gap-3">
        <CustomBarChartComponent
          title="Top Complaints"
          description="January - June 2024"
          data={complaintsData}
          config={chartConfigCommon}

        />

        <CustomBarChartComponent
          title="Top Improvements"
          description="January - June 2024"
          data={improvementsData}
          config={chartConfigCommon}

        />

        <CustomBarChartComponent
          title="Top Praises"
          description="January - June 2024"
          data={praisesData}
          config={chartConfigCommon}

        />
      </div>
    </div>
  );
}
