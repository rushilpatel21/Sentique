"use client"

import { useState, useEffect } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import {getLast6Month} from "@/pages/Dashboard/api.ts";

export function Overview() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getLast6Month("default");
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return <div className="h-[350px] flex items-center justify-center">Loading...</div>;
  }

  if (error) {
    return <div className="h-[350px] flex items-center justify-center text-red-500">{error}</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={data}>
        <XAxis
          dataKey="month"
          stroke="#888888"
          fontSize={12}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          stroke="#888888"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => `${value}`}
        />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="positive"
          stroke="#8884d8"
          strokeWidth={2}
          activeDot={{ r: 8 }}
        />
        <Line
          type="monotone"
          dataKey="negative"
          stroke="#82ca9d"
          strokeWidth={2}
        />
        <Line
          type="monotone"
          dataKey="neutral"
          stroke="#ffc658"
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}