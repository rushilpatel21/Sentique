import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs.tsx";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card.tsx";
import { Overview } from "@/components/overview.tsx";
import { RecentFeedback } from "@/components/recent-feedback.tsx";
import { FeedbackSources } from "@/components/feedback-sources.tsx";
import { SentimentAnalysis } from "@/components/sentiment-analysis.tsx";
import { ProductFeedback } from "@/components/product-feedback.tsx";
import { FeedbackDetails } from "@/components/feedback-details.tsx";
import { DateRangePicker } from "@/components/date-range-picker.tsx";
import { TimeFilter } from "@/components/time-filter.tsx";
import { TrendingTopics } from "@/components/trending-topics.tsx";
import { Button } from "@/components/ui/button.tsx";
import { RefreshCw } from "lucide-react";
import { DateRange } from "react-day-picker";
import {getStats} from "@/pages/Dashboard/api.ts";
import {ScrollArea} from "@/components/ui/scroll-area.tsx";
import {FeedbackSourcesDetailed} from "@/components/feedback-sources-detailed.tsx";

export function Dashboard() {
  const [dateRange, setDateRange] = useState<DateRange>({
    from: new Date(2024, 0, 1),
    to: new Date(),
  });
  const [timeFilter, setTimeFilter] = useState('ALL');
  const [stats, setStats] = useState({
    total_feedback: 0,
    top_source: "N/A",
    most_common_sentiment: "N/A"
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getStats(timeFilter);

      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [timeFilter]);

  const changeTime = (time: string) => {
    setTimeFilter(time);
  };

  return (
    <div className="flex min-h-screen flex-col">
      <div className="border-b">
        <div className="flex h-16 items-center justify-end px-6">
          {/*<div className="flex items-center gap-2">*/}
          {/*  <TimeFilter setTimeFilter={changeTime} />*/}
          {/*  {timeFilter === 'custom' && (*/}
          {/*    <DateRangePicker*/}
          {/*      dateRange={dateRange}*/}
          {/*      setDateRange={setDateRange}*/}
          {/*    />*/}
          {/*  )}*/}
          {/*</div>*/}
          <Button
            variant="outline"
            size="sm"
            onClick={fetchStats}
            disabled={loading}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Refreshing...' : 'Refresh Data'}
          </Button>
        </div>
      </div>
      <div className="flex-1 space-y-4 pt-2 px-6">
        {error && (
          <div className="p-4 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="sentiment">Sentiment Analysis</TabsTrigger>
            <TabsTrigger value="product">Product Feedback</TabsTrigger>
            <TabsTrigger value="details">Feedback Details</TabsTrigger>
          </TabsList>
          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Feedback</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {loading ? 'Loading...' : (stats?.total_feedback ?? 'N/A')}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Most Common Sentiment</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {loading ? 'Loading...' : (stats?.most_common_sentiment ?? 'N/A')}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Top Feedback Source</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {loading ? 'Loading...' : (stats?.top_source ?? 'N/A')}
                  </div>
                </CardContent>
              </Card>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
              <Card className="col-span-4">
                <CardHeader>
                  <CardTitle>Sentiment Overview</CardTitle>
                </CardHeader>
                <CardContent className="pl-2">
                  <Overview />
                </CardContent>
              </Card>
              <Card className="col-span-3">
                <CardHeader>
                  <CardTitle>Trending Topics</CardTitle>
                  <CardDescription>Most discussed topics in the last 30 days</CardDescription>
                </CardHeader>
                <CardContent>
                  <TrendingTopics />
                </CardContent>
              </Card>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
              <Card className="col-span-4">
                <CardHeader>
                  <CardTitle>Recent Feedback</CardTitle>
                  <CardDescription>Latest feedback from all sources</CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[350px] pr-4">
                  <RecentFeedback />
                  </ScrollArea>
                </CardContent>
              </Card>
              <Card className="col-span-3">
                <CardHeader>
                  <CardTitle>Feedback Sources</CardTitle>
                  <CardDescription>Distribution of feedback by source</CardDescription>
                </CardHeader>
                <CardContent>
                  <FeedbackSources />
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          <TabsContent value="sentiment" className="space-y-4">
            <SentimentAnalysis />
          </TabsContent>
          <TabsContent value="product" className="space-y-4">
            <ProductFeedback />
          </TabsContent>
          <TabsContent value="details" className="space-y-4">
            <FeedbackDetails />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}