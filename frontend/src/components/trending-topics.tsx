"use client"

import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { getTrendingTopic } from "@/pages/Dashboard/api.ts";

export function TrendingTopics({ timeFilter }: { timeFilter: string }) {
  const [topics, setTopics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTrendingTopics = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getTrendingTopic(timeFilter);
      // Ensure we always have an array, even if the API returns null
      setTopics(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error fetching trending topics:", err);
      setError(err instanceof Error ? err.message : 'An error occurred');
      setTopics([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrendingTopics();
  }, [timeFilter]);

  if (loading) {
    return <div>Loading trending topics...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  // Safely calculate max count with fallback
  const maxCount = topics.length > 0 
    ? Math.max(...topics.map((item) => item.last_30_days_mentions || 0), 1) 
    : 1;

  return (
    <div className="space-y-4">
      {topics.length > 0 ? (
        topics.map((item) => (
          <div key={item.category} className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{item.category}</span>
              <Badge variant={item.sentiment === "positive" ? "default" : "destructive"}>
                {item.last_30_days_mentions} mentions
              </Badge>
            </div>
            <Progress 
              value={(item.last_30_days_mentions / maxCount) * 100} 
              className="h-2" 
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>{item.trend_direction}</span>
              <span>{item.sentiment}</span>
            </div>
          </div>
        ))
      ) : (
        <div>No trending topics available</div>
      )}
    </div>
  );
}