import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend, Line, LineChart, Cell } from "recharts";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getFeedbackDetailedSources } from "@/pages/Dashboard/api.ts";

interface FeedbackSourcesProps {
  detailed?: boolean;
}

export function FeedbackSourcesDetailed({ detailed = true }: FeedbackSourcesProps) {
  const [sourcesData, setSourcesData] = useState([]);
  const [sourcesOverTimeData, setSourcesOverTimeData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Colors for each source
  const colors = {
    "googleplay": "#4285F4",
    "appstore": "#FF4500",
    "twitter": "#1DA1F2",
    "reddit": "#A2AAAD",
    "trustpilot": "#00B67A"
  };

  // Display names for sources
  const sourceDisplayNames = {
    "googleplay": "Google Play",
    "appstore": "App Store",
    "twitter": "Twitter/X",
    "reddit": "Reddit",
    "trustpilot": "Trust Pilot"
  };

  const fetchFeedbackSources = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getFeedbackDetailedSources();
      console.log("Received data:", data);

      // Add colors to sources data
      const enrichedSources = data.sources.map((item: any) => ({
        source: item.source,
        count: item.count,
        color: colors[item.source] || "#8884d8"
      }));
      setSourcesData(enrichedSources);

      // Process the over time data
      // Create a new array with the correct property names
      const transformedOverTimeData = data.sources_over_time.map((item: any) => ({
        month: item.month,
        // Map the API keys to the keys expected by the chart
        googleplay: item.Playstore,
        reddit: item.Reddit,
        twitter: item.X,
        appstore: item.AppStore,
        trustpilot: item["Trust Pilot"]
      }));

      setSourcesOverTimeData(transformedOverTimeData);
      console.log("Transformed over time data:", transformedOverTimeData);
    } catch (err) {
      console.error("Error in fetchFeedbackSources:", err);
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeedbackSources();
  }, []);

  if (loading) return <div className="flex justify-center items-center h-64">Loading feedback sources...</div>;
  if (error) return <div className="flex justify-center items-center h-64 text-red-500">{error}</div>;
  if (!sourcesData.length) return <div className="flex justify-center items-center h-64">No feedback source data available</div>;

  const totalCount = sourcesData.reduce((sum: number, item: any) => sum + item.count, 0) || 1;

  // Simple chart for non-detailed view
  if (!detailed) {
    return (
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={sourcesData}>
          <XAxis dataKey="source" />
          <YAxis />
          <Tooltip formatter={(value, name) => [value, 'Count']} />
          <Bar dataKey="count" name="Feedback Count">
            {sourcesData.map((entry: any, index: number) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    );
  }

  // Check if all values in sources_over_time are zero
  const hasTimeData = sourcesOverTimeData.some(item =>
    item.googleplay > 0 || item.reddit > 0 || item.twitter > 0 ||
    item.appstore > 0 || item.trustpilot > 0
  );

  // Detailed view with multiple charts
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
              <Tooltip formatter={(value, name) => [value, 'Count']} />
              <Bar dataKey="count" name="Feedback Count">
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
          <CardDescription>Trend of feedback volume by source over the last 6 months</CardDescription>
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
                    <Line type="monotone" dataKey="googleplay" name="Google Play" stroke={colors.googleplay} strokeWidth={2} />
                    <Line type="monotone" dataKey="reddit" name="Reddit" stroke={colors.reddit} strokeWidth={2} />
                    <Line type="monotone" dataKey="twitter" name="Twitter/X" stroke={colors.twitter} strokeWidth={2} />
                    <Line type="monotone" dataKey="appstore" name="App Store" stroke={colors.appstore} strokeWidth={2} />
                    <Line type="monotone" dataKey="trustpilot" name="Trust Pilot" stroke={colors.trustpilot} strokeWidth={2} />
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
                    <Bar dataKey="googleplay" name="Google Play" fill={colors.googleplay} />
                    <Bar dataKey="reddit" name="Reddit" fill={colors.reddit} />
                    <Bar dataKey="twitter" name="Twitter/X" fill={colors.twitter} />
                    <Bar dataKey="appstore" name="App Store" fill={colors.appstore} />
                    <Bar dataKey="trustpilot" name="Trust Pilot" fill={colors.trustpilot} />
                  </BarChart>
                </ResponsiveContainer>
              </TabsContent>
            </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
