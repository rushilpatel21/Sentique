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
    }[];
    config?: ChartConfig;
}

const BarChartComponent: React.FC<BarChartProps> = ({ title, description, data, config = {} }) => {
    return (
        <Card className="max-w-[400px]-h-[200px]">
            <CardHeader>
                <CardTitle>{title}</CardTitle>
                <CardDescription>{description}</CardDescription>
            </CardHeader>
            <CardContent className="w-full h-full">
                <ChartContainer config={config} className="w-full h-full">
                    <BarChart
                        width={450}
                        height={250}
                        accessibilityLayer
                        data={data}
                        layout="vertical"
                        margin={{ top: 5, right: 5, left: 30, bottom: 5 }} // More space for Y-axis labels
                    >
                        <YAxis
                            dataKey={(entry) => entry.browser || entry.reason} // Supports both `browser` and `reason`
                            type="category"
                            tickLine={false}
                            tickMargin={10}
                            axisLine={false}
                            tickFormatter={(value) =>
                                String(config?.[value as keyof typeof config]?.label || value)
                            }
                            fontSize={15}
                            tick={{
                                style: {
                                    whiteSpace: "nowrap", // Keeps label on one line
                                    overflow: "hidden", // Hides overflowing text
                                    textOverflow: "ellipsis", // Adds '...' if label is too long
                                    maxWidth: "100%", // Ensures no wrapping
                                },
                            }}
                            width={80} // Adjusts width for the Y-axis label container
                           
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
