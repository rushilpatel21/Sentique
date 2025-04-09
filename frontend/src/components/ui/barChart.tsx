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
        month?: string;
    }[];
    config?: ChartConfig;
}

const BarChartComponent: React.FC<BarChartProps> = ({ title, description, data, config = {} }) => {
    // Custom tick renderer for Y-axis that ensures left alignment
    const CustomYAxisTick = ({ y, payload, textColor = "#71717a" }: any) => {
        const label = config?.[payload.value as keyof typeof config]?.label || payload.value;
        
        return (
            <g transform={`translate(0,${y})`}>
                <text
                    x={10}
                    y={0}
                    dy={4}
                    textAnchor="start"
                    fontSize={15}
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
    };

    return (
        <Card className="max-w-[400px]-h-[200px]">
            <CardHeader>
                <CardTitle>{title}</CardTitle>
                <CardDescription>{description}</CardDescription>
            </CardHeader>
            <CardContent className="w-full h-full">
                <ChartContainer config={config} className="w-full h-full">
                    <BarChart
                        width={600} 
                        height={400}
                        accessibilityLayer
                        data={data}
                        layout="vertical"
                        margin={{ top: 5, right: 5, left: 20, bottom: 5 }} // Increased left margin for labels
                    >
                        <YAxis
                            dataKey={(entry) => entry.browser || entry.reason || entry.month} // Supports browser, reason, and month
                            type="category"
                            tickLine={false}
                            axisLine={false}
                            tick={<CustomYAxisTick />} // Use custom tick renderer
                            width={70} // Increased width for the Y-axis label container
                        />

                        <XAxis
                            dataKey={(entry) => entry.visitors || entry.count}
                            type="number"
                            hide
                        />
                        <ChartTooltip cursor={false} content={<ChartTooltipContent hideLabel />} />
                        <Bar dataKey={(entry) => entry.visitors || entry.count} layout="vertical" radius={5}>
                            <LabelList
                                dataKey={(entry) => entry.visitors || entry.count}
                                position="insideRight"
                                fill="white"
                                fontSize={15}
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

export default BarChartComponent;