import { Bar, BarChart, XAxis, YAxis, LabelList, ResponsiveContainer } from "recharts";
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
import { useTheme } from "@/components/theme-provider"; 

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
  className?: string; // Add className prop for custom container styling
}

const CustomBarChartComponent: React.FC<BarChartProps> = ({ 
  title, 
  description, 
  data, 
  config = {},
  className = "",
}) => {
  const { theme } = useTheme();

  // Set colors dynamically based on the theme
  const textColor = theme === "dark" ? "white" : "black";
  const tooltipBg = theme === "dark" ? "black" : "white";
  const tooltipTextColor = theme === "dark" ? "white" : "black";

  return (
    <Card className={`w-full h-auto ${className}`}>
      <CardHeader className="p-4">
        <CardTitle className="text-lg">{title}</CardTitle>
        <CardDescription className="text-sm">{description}</CardDescription>
      </CardHeader>
      <CardContent className="p-0 pb-4">
        {/* Fixed height container with responsive behavior */}
        <div className="w-full h-64">
          <ResponsiveContainer width="100%" height="100%">
            <ChartContainer config={config} className="w-full h-full">
              <BarChart
                accessibilityLayer
                data={data}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 30, bottom: 5 }}
              >
                <YAxis
                  dataKey={(entry) => entry.browser || entry.reason}
                  type="category"
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => String(config?.[value as keyof typeof config]?.label || value)}
                  fontSize={10}
                  tickMargin={15}
                  tick={(props) => {
                    const { y, payload } = props;
                    const value = payload.value;
                    const label = String(config?.[value as keyof typeof config]?.label || value);

                    return (
                      <g transform={`translate(0,${y})`}>
                        <text
                          x={10}
                          y={0}
                          dy={4}
                          textAnchor="start"
                          fontSize={10}
                          fill={textColor}
                          style={{
                            whiteSpace: "nowrap",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            maxWidth: "140px" // Limit text width
                          }}
                        >
                          {label}
                        </text>
                      </g>
                    );
                  }}
                  width={140} // Reduced from 160 to save space
                />

                <XAxis
                  dataKey={(entry: { visitors?: number; count?: number }) => entry.visitors || entry.count}
                  type="number"
                  hide
                />

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
                  radius={4}
                  fill={(data[0] && (data[0].fill || data[0].color)) || "#000"}
                >
                  <LabelList
                    dataKey={(entry) => entry.visitors || entry.count}
                    position="right"
                    fill={textColor}
                    fontSize={10}
                  />
                </Bar>
              </BarChart>
            </ChartContainer>
          </ResponsiveContainer>
        </div>
      </CardContent>
      <CardFooter className="py-2 px-4 text-xs text-center">
        <div className="leading-none text-muted-foreground w-full">
          Count of Feedback Records
        </div>
      </CardFooter>
    </Card>
  );
};

export default CustomBarChartComponent;