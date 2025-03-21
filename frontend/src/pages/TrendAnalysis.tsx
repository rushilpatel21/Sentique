import React from "react";
import ButtonGroup from "@/components/ui/ButtonGroup";
import BarChartComponent from "@/components/ui/barChart";
import Summary from "@/components/ui/graphsummary";
import DropdownFromTrendPage from "@/components/ui/DropdownFromTrendPage ";

// Sample data for the graphs
const chartData1 = [
    { month: "Jan", visitors: 50 },
    { month: "Feb", visitors: 75 },
    { month: "Mar", visitors: 60 },
    { month: "Apr", visitors: 90 },
    { month: "May", visitors: 120 },
];

const chartData2 = [
    { month: "Jan", visitors: 40 },
    { month: "Feb", visitors: 55 },
    { month: "Mar", visitors: 70 },
    { month: "Apr", visitors: 80 },
    { month: "May", visitors: 110 },
];

// Common chart config (example of width, height, and margin settings)
const chartConfig1 = {
    visitors: { label: "Visitors" },
    chrome: { label: "Playstore", color: "hsl(var(--chart-1))" },
    safari: { label: "Reddit", color: "hsl(var(--chart-2))" },
    firefox: { label: "X", color: "hsl(var(--chart-3))" },
    edge: { label: "AppStore", color: "hsl(var(--chart-4))" },
    other: { label: "Trust Pilot", color: "hsl(var(--chart-5))" },
};

import { useState } from "react";

const TrendAnalysis: React.FC = () => {

    // Store selected category from dropdown
    const [selectedCategory, setSelectedCategory] = useState("Default");

    return (
        <div className="trend-analysis-container">

            <div className="mt-6 flex items-center gap-6 justify-between">
                {/* Button Group (left side) */}
                <ButtonGroup defaultSelected="DEFAULT" onSelectionChange={() => { }} />

                {/* Dropdown Menu (right side) */}
                <div className="ml-auto">
                    <DropdownFromTrendPage onChange={(category: string) => setSelectedCategory(category)} />
                </div>
            </div>


            {/* Graphs Section - Side by Side */}
            <div className="mt-6 grid grid-cols-2 gap-4">
                <BarChartComponent
                    title={`Positive Feedback (${selectedCategory})`}
                    description="January - June 2024"
                    data={chartData1.map(item => ({
                        ...item,
                        fill: "#8884d8", // Color for the bars
                    }))}
                    config={chartConfig1}
                />
                <BarChartComponent
                    title={`Negative Feedback (${selectedCategory})`}
                    description="January - June 2024"
                    data={chartData2.map(item => ({
                        ...item,
                        fill: "#82ca9d", // Different color for the second chart
                    }))}
                    config={chartConfig1}
                />
            </div>

            {/* Add Space Between Graphs and Summary */}
            <div className="mt-7">
                <Summary graphData={{ data1: chartData1, data2: chartData2 }} />
            </div>

        </div>
    );
};

export default TrendAnalysis;
