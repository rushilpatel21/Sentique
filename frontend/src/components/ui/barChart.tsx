import { TrendingUp } from "lucide-react";
import { Bar, BarChart, XAxis, YAxis, LabelList } from "recharts"; // Import LabelList

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

// Chart data and config setup
const chartData = [
    { browser: "chrome", visitors: 275, fill: "var(--color-chrome)" },
    { browser: "safari", visitors: 200, fill: "var(--color-safari)" },
    { browser: "firefox", visitors: 187, fill: "var(--color-firefox)" },
    { browser: "edge", visitors: 173, fill: "var(--color-edge)" },
    { browser: "other", visitors: 90, fill: "var(--color-other)" },
];

const chartConfig = {
    visitors: {
        label: "Visitors",
    },
    chrome: {
        label: "Playstore",
        color: "hsl(var(--chart-1))",
    },
    safari: {
        label: "Reddit",
        color: "hsl(var(--chart-2))",
    },
    firefox: {
        label: "X",
        color: "hsl(var(--chart-3))",
    },
    edge: {
        label: "AppStore",
        color: "hsl(var(--chart-4))",
    },
    other: {
        label: "Trust Pilot",
        color: "hsl(var(--chart-5))",
    },
} satisfies ChartConfig;

// Bar Chart Component
const BarChartComponent = () => {
    return (
        <Card className="max-w-[400px]-h-[100px]">
            <CardHeader>
                <CardTitle>Sources of Feedback</CardTitle>
                <CardDescription>January - June 2024</CardDescription>
            </CardHeader>
            <CardContent className ="w-full h-full">
                <ChartContainer config={chartConfig} className="w-full h-full">
                    <BarChart
                         width={450} // Increased width
                         height={250} // Increased height
                        accessibilityLayer
                        data={chartData}
                        layout="vertical"
                        margin={{
                            top: 5,
                            right: 5,
                            left: 10,
                            bottom: 5,
                        }}
                    >
                        <YAxis
                            dataKey="browser"
                            type="category"
                            tickLine={false}
                            tickMargin={10}
                            axisLine={false}
                            tickFormatter={(value) =>
                                chartConfig[value as keyof typeof chartConfig]?.label
                            }
                        />
                        <XAxis dataKey="visitors" type="number" hide />
                        <ChartTooltip
                            cursor={false}
                            content={<ChartTooltipContent hideLabel />}
                        />
                        <Bar dataKey="visitors" layout="vertical" radius={5}>
                            {/* Position label inside the bar for better visibility */}
                            <LabelList dataKey="visitors" position="insideRight" fill="white" fontSize={12} />
                        </Bar>

                    </BarChart>
                </ChartContainer>
            </CardContent>
            <CardFooter className="flex flex-col items-center gap-2 text-sm">
                <div className="leading-none text-muted-foreground text-center" >
                    Count of Feedback Records
                </div>
            </CardFooter>
        </Card>
    );
};

// Export the BarChartComponent as default
export default BarChartComponent;
