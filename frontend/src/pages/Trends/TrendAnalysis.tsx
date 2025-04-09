"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { DateRangePicker } from "@/components/date-range-picker"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RefreshCw } from "lucide-react"
import { toast } from "sonner"
import { DateRange } from "react-day-picker"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { generateTrendAnalysis } from "@/services/trendsService"

const categories = [
  "Ride Availability",
  "Payment & Transactions",
  "Driver Experience",
  "Pricing",
  "User Interface",
  "App Performance",
  "Customer Support",
  "Company Policies",
  "Regulations & Legal",
  "Security",
  "Trust & Safety",
  "Discounts & Offers"
]

const timePresets = [
  { label: "Daily", value: "daily" },
  { label: "Weekly", value: "weekly" },
  { label: "Monthly", value: "monthly" },
  { label: "Quarterly", value: "quarterly" },
  { label: "Custom Range", value: "custom" }
]

export function TrendAnalysis() {
  const [dateRange, setDateRange] = useState<DateRange>({
    from: new Date(new Date().setMonth(new Date().getMonth() - 1)), // Default to last month
    to: new Date(), // Today
  })
  const [selectedCategory, setSelectedCategory] = useState<string>(categories[0])
  const [selectedTimePreset, setSelectedTimePreset] = useState<string>("monthly")
  const [isLoading, setIsLoading] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<{
    positiveInsights: string[],
    negativeInsights: string[],
    summary: string,
    metadata?: {
      reviewCount: number,
      dateRange: {
        from: string,
        to: string
      },
      category: string
    }
  } | null>(null)

  const handleGenerateAnalysis = async () => {
    if (selectedTimePreset === "custom" && (!dateRange.from || !dateRange.to)) {
      toast.error("Please select a valid date range")
      return
    }

    setIsLoading(true)
    try {
      const result = await generateTrendAnalysis(
        selectedCategory, 
        dateRange, 
        selectedTimePreset !== "custom" ? selectedTimePreset : undefined
      )
      
      setAnalysisResults(result)
      toast.success("Analysis generated successfully")
    } catch (error) {
      console.error("Error generating analysis:", error)
      toast.error("Failed to generate analysis. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  // Handle time preset changes
  const handleTimePresetChange = (value: string) => {
    setSelectedTimePreset(value)
    
    // If not custom, set the dateRange based on preset
    if (value !== "custom") {
      const today = new Date()
      let fromDate = new Date()
      
      switch(value) {
        case "daily":
          fromDate.setDate(today.getDate() - 1)
          break
        case "weekly":
          fromDate.setDate(today.getDate() - 7)
          break
        case "monthly":
          fromDate.setMonth(today.getMonth() - 1)
          break
        case "quarterly":
          fromDate.setMonth(today.getMonth() - 3)
          break
      }
      
      setDateRange({
        from: fromDate,
        to: today
      })
    }
  }

  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Trend Analysis</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Analysis Parameters</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger id="category">
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map(category => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Time Range</Label>
              <RadioGroup 
                value={selectedTimePreset} 
                onValueChange={handleTimePresetChange}
                className="flex flex-col space-y-1"
              >
                {timePresets.map(preset => (
                  <div key={preset.value} className="flex items-center space-x-2">
                    <RadioGroupItem value={preset.value} id={`preset-${preset.value}`} />
                    <Label htmlFor={`preset-${preset.value}`}>{preset.label}</Label>
                  </div>
                ))}
              </RadioGroup>
            </div>

            {selectedTimePreset === "custom" && (
              <div className="space-y-2">
                <Label>Custom Date Range</Label>
                <DateRangePicker 
                  dateRange={dateRange} 
                  setDateRange={setDateRange} 
                  className="w-full" 
                />
              </div>
            )}
          </CardContent>
          <CardFooter>
            <Button 
              className="w-full" 
              onClick={handleGenerateAnalysis} 
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  Generate Analysis
                </>
              )}
            </Button>
          </CardFooter>
        </Card>

        <Card className="col-span-1 md:col-span-2">
          <CardHeader>
            <CardTitle>
              Analysis Results
              {analysisResults?.metadata && (
                <span className="block text-sm font-normal text-muted-foreground mt-1">
                  Based on {analysisResults.metadata.reviewCount} reviews • {new Date(analysisResults.metadata.dateRange.from).toLocaleDateString()} - {new Date(analysisResults.metadata.dateRange.to).toLocaleDateString()}
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {analysisResults ? (
              <Tabs defaultValue="summary">
                <TabsList className="mb-4">
                  <TabsTrigger value="summary">Summary</TabsTrigger>
                  <TabsTrigger value="insights">Insights</TabsTrigger>
                </TabsList>
                
                <TabsContent value="summary" className="space-y-4">
                  <div className="p-4 bg-muted rounded-lg">
                    <h3 className="text-lg font-semibold mb-2">Summary for {selectedCategory}</h3>
                    <p className="text-pretty">{analysisResults.summary}</p>
                  </div>
                </TabsContent>
                
                <TabsContent value="insights" className="space-y-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">What Users Like</h3>
                    <div className="space-y-2">
                      {analysisResults.positiveInsights.map((insight, index) => (
                        <div key={`pos-insight-${index}`} className="p-3 bg-green-50 border border-green-200 rounded-md text-green-800">
                          {insight}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Areas for Improvement</h3>
                    <div className="space-y-2">
                      {analysisResults.negativeInsights.map((insight, index) => (
                        <div key={`neg-insight-${index}`} className="p-3 bg-red-50 border border-red-200 rounded-md text-red-800">
                          {insight}
                        </div>
                      ))}
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
                <p>Select a category and time range, then click "Generate Analysis" to see results.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}