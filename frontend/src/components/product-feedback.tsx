import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend } from "recharts"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search } from "lucide-react"
import {getFeatureSpecificFeedback, getProductFeedbackCategories, getTopFeedbackTopics} from "@/pages/Dashboard/api.ts";


export function ProductFeedback() {
  const [productFeedbackData, setProductFeedbackData] = useState([]);
  const [topTags, setTopTags] = useState([]);
  const [featureFeedback, setFeatureFeedback] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Fetch all data in parallel
        const [categoriesResponse, topicsResponse, featuresResponse] = await Promise.all([
          getProductFeedbackCategories(),
          getTopFeedbackTopics(),
          getFeatureSpecificFeedback()
        ]);


        // Check if responses have the expected structure
        if (categoriesResponse && Array.isArray(categoriesResponse)) {
          setProductFeedbackData(categoriesResponse);
        } else if (categoriesResponse && Array.isArray(categoriesResponse.data)) {
          setProductFeedbackData(categoriesResponse.data);
        } else {
          console.error("Invalid categories data format:", categoriesResponse);
          setProductFeedbackData([]);
        }

        if (topicsResponse && Array.isArray(topicsResponse)) {
          setTopTags(topicsResponse);
        } else if (topicsResponse && Array.isArray(topicsResponse.data)) {
          setTopTags(topicsResponse.data);
        } else {
          console.error("Invalid topics data format:", topicsResponse);
          setTopTags([]);
        }

        if (featuresResponse && Array.isArray(featuresResponse)) {
          setFeatureFeedback(featuresResponse);
        } else if (featuresResponse && Array.isArray(featuresResponse.data)) {
          setFeatureFeedback(featuresResponse.data);
        } else {
          console.error("Invalid features data format:", featuresResponse);
          setFeatureFeedback([]);
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError("Failed to load data. Please try again later.");
        setProductFeedbackData([]);
        setTopTags([]);
        setFeatureFeedback([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filter out tags with null sentiment and match search term
  const filteredTags = topTags.filter(tag =>
    tag &&
    tag.name &&
    tag.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
    tag.sentiment !== null
  );

  // Calculate percentage for feature feedback
  const calculatePercentage = (positive, negative) => {
    const total = positive + negative;
    if (total === 0) return 0;
    return Math.round((positive / total) * 100);
  };

  if (isLoading) {
    return <div className="flex justify-center items-center h-64">Loading product feedback data...</div>;
  }

  if (error) {
    return <div className="flex justify-center items-center h-64 text-red-500">{error}</div>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
      <Card className="col-span-4">
        <CardHeader>
          <CardTitle>Product Feedback Categories</CardTitle>
          <CardDescription>Feedback distribution by product category</CardDescription>
        </CardHeader>
        <CardContent className="pl-2">
          {productFeedbackData && productFeedbackData.length > 0 ? (
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={productFeedbackData} layout="vertical">
                <XAxis type="number" />
                <YAxis dataKey="category" type="category" width={100} />
                <Tooltip />
                <Legend />
                <Bar dataKey="positive" name="Positive Feedback" fill="#4ade80" />
                <Bar dataKey="negative" name="Negative Feedback" fill="#f87171" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex justify-center items-center h-64">No category data available</div>
          )}
        </CardContent>
      </Card>
      <Card className="col-span-3">
        <CardHeader>
          <CardTitle>Top Feedback Topics</CardTitle>
          <CardDescription>Most mentioned topics in user feedback</CardDescription>
          <div className="flex w-full max-w-sm items-center space-x-2 mt-2">
            <Input placeholder="Search topics..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
            <Button type="submit" size="icon">
              <Search className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {filteredTags && filteredTags.length > 0 ? (
              filteredTags.map((tag) => (
                <Badge
                  key={tag.name}
                  variant={
                    tag.sentiment === "positive" ? "default" : tag.sentiment === "negative" ? "destructive" : "outline"
                  }
                  className="text-sm py-1 px-2"
                >
                  {tag.name} ({tag.count})
                </Badge>
              ))
            ) : (
              <div className="text-sm text-gray-500">No topics with sentiment found. Try adjusting your search.</div>
            )}
          </div>
        </CardContent>
      </Card>
      <Card className="col-span-7">
        <CardHeader>
          <CardTitle>Feature-Specific Feedback</CardTitle>
          <CardDescription>Detailed feedback analysis by product feature</CardDescription>
        </CardHeader>
        <CardContent>
          {featureFeedback && featureFeedback.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {featureFeedback
                .filter(feature => feature.positive > 0 || feature.negative > 0) // Only show features with feedback
                .map((feature) => {
                  const percentPositive = calculatePercentage(feature.positive, feature.negative);
                  return (
                    <div key={feature.name} className="flex flex-col p-4 border rounded-lg">
                      <h3 className="text-lg font-semibold">{feature.name}</h3>
                      <div className="flex items-center mt-2">
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                          <div
                            className="bg-green-500 h-2.5 rounded-full"
                            style={{ width: `${percentPositive}%` }}
                          ></div>
                        </div>
                        <span className="ml-2 text-sm font-medium">
                          {percentPositive}% Positive
                        </span>
                      </div>
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>Total: {feature.positive + feature.negative}</span>
                        <span>👍 {feature.positive} | 👎 {feature.negative}</span>
                      </div>
                    </div>
                  );
                })}
            </div>
          ) : (
            <div className="flex justify-center items-center h-64">No feature feedback available</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
