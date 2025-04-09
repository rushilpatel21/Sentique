import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Bookmark, MessageSquare } from "lucide-react";
import {getRecentFeedback} from "@/pages/Dashboard/api.ts";

export function RecentFeedback({ timeFilter }: { timeFilter: string }) {
  const [feedback, setFeedback] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRecentFeedback = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getRecentFeedback(timeFilter);
      setFeedback(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecentFeedback();
  }, [timeFilter]);

  if (loading) return <div>Loading recent feedback...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="space-y-8">
      {feedback.map((item: any) => (
        <div key={item.id} className="flex items-start gap-4">
          <div className="grid gap-1">
            <div className="flex items-center gap-2">
              <div className="font-semibold">{item.username}</div>
              <div className="text-xs text-muted-foreground">{item.date}</div>
              <Badge variant={item.sentiment === "positive" ? "default" : "destructive"} className="ml-auto">
                {item.sentiment !== null ? item.sentiment : "N/A"}
              </Badge>
            </div>
            <div className="text-sm text-muted-foreground">
              via <span className="font-medium">{item.source}</span>
            </div>
            <div className="text-sm">{item.review}</div>
            <div className="flex items-center gap-2 pt-1">
              <Button variant="ghost" size="sm" className="h-7 px-2">
                <Bookmark className="mr-1 h-3.5 w-3.5" />
                Save
              </Button>
              <Button variant="ghost" size="sm" className="h-7 px-2">
                <MessageSquare className="mr-1 h-3.5 w-3.5" />
                Reply
              </Button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}