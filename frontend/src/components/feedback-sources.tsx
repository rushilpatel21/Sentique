import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend, Line, LineChart, Cell } from "recharts";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getFeedbackSources } from "@/pages/Dashboard/api.ts";

interface FeedbackSourcesProps {
  detailed?: boolean;
  timeFilter: string;
}

export function FeedbackSources({ detailed = false, timeFilter }: FeedbackSourcesProps) {
  const [sourcesData, setSourcesData] = useState([]);
  const [sourcesOverTimeData, setSourcesOverTimeData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const colors = {
    "appstore": "#4285F4",
    "googleplay": "#FF4500",
    "twitter": "#1DA1F2",
    "reddit": "#A2AAAD",
    "trustpilot": "#00B67A"
  };

  const fetchFeedbackSources = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getFeedbackSources(timeFilter);

      // Enrich sources data with colors
      const enrichedSources = data.sources.map((item: any) => ({
        ...item,
        color: colors[item.source] || "#8884d8"
      }));
      setSourcesData(enrichedSources);

      // Transform sources_over_time to match colors object keys
      const transformedOverTimeData = data.sources_over_time.map((item: any) => ({
        month: item.month,
        googleplay: item.Playstore,
        reddit: item.Reddit,
        twitter: item.X,
        appstore: item.AppStore,
        trustpilot: item["Trust Pilot"]
      }));
      setSourcesOverTimeData(transformedOverTimeData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeedbackSources();
  }, [timeFilter]);

  if (loading) return <div>Loading feedback sources...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  const totalCount = sourcesData.reduce((sum: number, item: any) => sum + item.count, 0) || 1;

  if (!detailed) {
    return (
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={sourcesData}>
          <XAxis dataKey="source" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count">
            {sourcesData.map((entry: any, index: number) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
      <Card className="col-span-4">
        <CardHeader>
          <CardTitle>Feedback Volume by Source</CardTitle>
          <CardDescription>Number of feedback entries from each source</CardDescription>
        </CardHeader>
        <CardContent className="pl-2">
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={sourcesData} layout="vertical">
              <XAxis type="number" />
              <YAxis dataKey="source" type="category" width={100} />
              <Tooltip />
              <Bar dataKey="count">
                {sourcesData.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      <Card className="col-span-3">
        <CardHeader>
          <CardTitle>Source Distribution</CardTitle>
          <CardDescription>Percentage breakdown of feedback sources</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sourcesData.map((source: any) => (
              <div key={source.source} className="flex items-center">
                <div className="w-16 text-sm">{source.source}</div>
                <div className="w-full ml-2">
                  <div className="h-2 bg-gray-200 rounded-full">
                    <div
                      className="h-2 rounded-full"
                      style={{
                        width: `${(source.count / totalCount) * 100}%`,
                        backgroundColor: source.color,
                      }}
                    ></div>
                  </div>
                </div>
                <div className="ml-2 text-sm font-medium">{Math.round((source.count / totalCount) * 100)}%</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      <Card className="col-span-7">
        <CardHeader>
          <CardTitle>Feedback Sources Over Time</CardTitle>
          <CardDescription>Trend of feedback volume by source over time</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="line">
            <TabsList>
              <TabsTrigger value="line">Line Chart</TabsTrigger>
              <TabsTrigger value="bar">Bar Chart</TabsTrigger>
            </TabsList>
            <TabsContent value="line" className="pt-4">
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={sourcesOverTimeData}>
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="googleplay" stroke={colors.googleplay} strokeWidth={2} />
                  <Line type="monotone" dataKey="reddit" stroke={colors.reddit} strokeWidth={2} />
                  <Line type="monotone" dataKey="twitter" stroke={colors.twitter} strokeWidth={2} />
                  <Line type="monotone" dataKey="appstore" stroke={colors.appstore} strokeWidth={2} />
                  <Line type="monotone" dataKey="trustpilot" stroke={colors.trustpilot} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </TabsContent>
            <TabsContent value="bar" className="pt-4">
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={sourcesOverTimeData}>
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="googleplay" fill={colors.googleplay} />
                  <Bar dataKey="reddit" fill={colors.reddit} />
                  <Bar dataKey="twitter" fill={colors.twitter} />
                  <Bar dataKey="appstore" fill={colors.appstore} />
                  <Bar dataKey="trustpilot" fill={colors.trustpilot} />
                </BarChart>
              </ResponsiveContainer>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}