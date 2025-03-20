import { Bar, BarChart, XAxis, YAxis, LabelList } from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { useTheme } from "@/components/theme-provider"; // Assuming you have a theme provider

// Define prop types for reusability
interface BarChartProps {
  title: string;
  description: string;
  data: {
    browser?: string;
    reason?: string;
    visitors?: number;
    count?: number;
    fill?: string;
    color?: string;
  }[];
  config?: ChartConfig;
}

const CustomBarChartComponent: React.FC<BarChartProps> = ({ title, description, data, config = {} }) => {
  const { theme } = useTheme(); // Get the current theme (light/dark)

  // Set colors dynamically based on the theme
  const textColor = theme === "dark" ? "white" : "black";
  const tooltipBg = theme === "dark" ? "black" : "white";
  const tooltipTextColor = theme === "dark" ? "white" : "black";

  return (
    <Card className="max-w-[600px] h-[400px]">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="w-full h-full">
        <ChartContainer config={config} className="w-full h-full">
          <BarChart
            accessibilityLayer
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 0, bottom: 5 }} // Adjust margin for alignment
          >
            <YAxis
              dataKey={(entry) => entry.browser || entry.reason}
              type="category"
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => String(config?.[value as keyof typeof config]?.label || value)}
              fontSize={10}
              tickMargin={10}
              tick={(props) => {
                const { x, y, payload } = props;
                const value = payload.value;
                const label = String(config?.[value as keyof typeof config]?.label || value);

                return (
                  <g transform={`translate(0,${y})`}>
                    <text
                      x={0} // Align to the left
                      y={0}
                      dy={4}
                      textAnchor="start"
                      fontSize={10}
                      fill={textColor} // Dynamic text color
                      style={{
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis"
                      }}
                    >
                      {label}
                    </text>
                  </g>
                );
              }}
              width={160}
            />

            <XAxis
              dataKey={(entry: { visitors?: number; count?: number }) => entry.visitors || entry.count}
              type="number"
              hide
            />

            {/* Tooltip with dynamic colors */}
            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  hideLabel
                  style={{
                    backgroundColor: tooltipBg,
                    color: tooltipTextColor,
                    padding: "8px",
                    borderRadius: "5px"
                  }}
                />
              }
            />

            <Bar
              dataKey={(entry) => entry.visitors || entry.count}
              layout="vertical"
              radius={5}
              fill={(data[0] && (data[0].fill || data[0].color)) || "#000"}
            >
              <LabelList
                dataKey={(entry) => entry.visitors || entry.count}
                position="right"
                fill={textColor} // Dynamically change label color
                fontSize={10}
              />
            </Bar>
          </BarChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex flex-col items-center gap-2 text-sm">
        <div className="leading-none text-muted-foreground text-center">
          Count of Feedback Records
        </div>
      </CardFooter>
    </Card>
  );
};

export default CustomBarChartComponent;
