"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DateRangePicker } from "@/components/date-range-picker"
import { Calendar, Download, RefreshCw } from "lucide-react"
import { Separator } from "@/components/ui/separator"
import { Checkbox } from "@/components/ui/checkbox"
import { DateRange } from "react-day-picker"
import { generateReport } from "@/pages/Dashboard/api.ts"

export function ViewReport() {
  const [dateRange, setDateRange] = useState<DateRange>({
    from: new Date(2024, 0, 1), // Default value
    to: new Date(2024, 5, 30),   // Default value
  })
  const [isGenerating, setIsGenerating] = useState(false)
  const [timeFilter, setTimeFilter] = useState("custom")

  // Create state for section checkboxes to ensure React properly manages them
  const [selectedSections, setSelectedSections] = useState({
    executive_summary: true,
    sentiment_analysis: true,
    feedback_sources: true,
    product_feedback: true,
    detailed_feedback: true
  });

  const handleGenerateReport = async () => {
    setIsGenerating(true)

    try {
      // Collect selected sections
      const sections = Object.entries(selectedSections)
        .filter(([_, isSelected]) => isSelected)
        .map(([section]) => section);
      
      // Log which sections will be used
      console.log("Selected sections for report:", sections);
      
      // Ensure we have at least one section selected
      if (sections.length === 0) {
        sections.push("executive_summary"); // Default to include at least one section
      }

      // Format the dates for better display
      const formatDate = (date) => {
        if (!date) return '';
        return new Date(date).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      };

      // Send request to backend
      const config = {
        reportType: "comprehensive", // Fixed to comprehensive
        timeFilter,  // This is correctly set based on user selection
        dateRange: {
          from: dateRange.from,
          to: dateRange.to,
          fromFormatted: formatDate(dateRange.from),
          toFormatted: formatDate(dateRange.to)
        },
        format: "pdf", // Fixed to PDF
        sections,
      }

      console.log("Starting report generation with config:", config);
      const reportBlob = await generateReport(config)
      console.log("Report received, preparing download...");

      // Create a download link
      const url = window.URL.createObjectURL(reportBlob)
      const a = document.createElement("a")
      a.href = url
      a.download = `comprehensive_report_${new Date().toISOString().split("T")[0]}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a) // Clean up the DOM
    } catch (error) {
      console.error("Error generating report:", error)
      alert(`Failed to generate report: ${error.message || 'Unknown error'}`)
    } finally {
      setIsGenerating(false)
    }
  }

  // Update the time period buttons to set the timeFilter
  const handleTimeFilterChange = (filter) => {
    setTimeFilter(filter)
    
    // Set appropriate date ranges based on filter
    const today = new Date()
    let fromDate = new Date()
    
    switch(filter) {
      case 'daily':
        // Set to today
        fromDate = new Date(today)
        break
      case 'weekly':
        // Set to 7 days ago
        fromDate = new Date(today)
        fromDate.setDate(today.getDate() - 7)
        break
      case 'monthly':
        // Set to 30 days ago
        fromDate = new Date(today)
        fromDate.setDate(today.getDate() - 30)
        break
      case 'quarterly':
        // Set to 90 days ago
        fromDate = new Date(today)
        fromDate.setDate(today.getDate() - 90)
        break
      default:
        // Don't change date range for custom
        return
    }
    
    setDateRange({
      from: fromDate,
      to: today
    })
  }

  // Handle section checkbox changes with React state
  const handleSectionChange = (section, checked) => {
    setSelectedSections(prev => ({
      ...prev,
      [section]: checked
    }));
  };

  return (
    <div className="flex flex-col min-h-screen">
      <div className="flex-1 p-4 md:p-6 space-y-4">
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="md:col-span-1">
            <CardHeader>
              <CardTitle>Report Configuration</CardTitle>
              <CardDescription>Configure your report settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Report Type</Label>
                <div className="p-2 border rounded-md bg-muted/50">
                  Comprehensive Report
                </div>
              </div>

              <div className="space-y-2">
                <Label>Time Period</Label>
                <div className="grid grid-cols-2 gap-2">
                  <Button 
                    variant={timeFilter === "daily" ? "default" : "outline"} 
                    size="sm" 
                    className="justify-start"
                    onClick={() => handleTimeFilterChange("daily")}
                  >
                    <Calendar className="mr-2 h-4 w-4" />
                    Daily
                  </Button>
                  <Button 
                    variant={timeFilter === "weekly" ? "default" : "outline"} 
                    size="sm" 
                    className="justify-start"
                    onClick={() => handleTimeFilterChange("weekly")}
                  >
                    <Calendar className="mr-2 h-4 w-4" />
                    Weekly
                  </Button>
                  <Button 
                    variant={timeFilter === "monthly" ? "default" : "outline"} 
                    size="sm" 
                    className="justify-start"
                    onClick={() => handleTimeFilterChange("monthly")}
                  >
                    <Calendar className="mr-2 h-4 w-4" />
                    Monthly
                  </Button>
                  <Button 
                    variant={timeFilter === "quarterly" ? "default" : "outline"} 
                    size="sm" 
                    className="justify-start"
                    onClick={() => handleTimeFilterChange("quarterly")}
                  >
                    <Calendar className="mr-2 h-4 w-4" />
                    Quarterly
                  </Button>
                </div>
                <div className="pt-2">
                  <DateRangePicker 
                    dateRange={dateRange} 
                    setDateRange={(newRange) => {
                      setDateRange(newRange)
                      setTimeFilter("custom") // When manually selecting dates, switch to custom
                    }} 
                    className="w-full" 
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-2">
                <Label>Report Format</Label>
                <div className="p-2 border rounded-md bg-muted/50">
                  PDF Document
                </div>
              </div>

              <div className="space-y-3">
                <Label>Include Sections</Label>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="executive_summary" 
                      checked={selectedSections.executive_summary}
                      onCheckedChange={(checked) => handleSectionChange('executive_summary', checked)}
                    />
                    <label
                      htmlFor="executive_summary"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      Executive Summary
                    </label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="sentiment_analysis" 
                      checked={selectedSections.sentiment_analysis}
                      onCheckedChange={(checked) => handleSectionChange('sentiment_analysis', checked)}
                    />
                    <label
                      htmlFor="sentiment_analysis"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      Sentiment Analysis
                    </label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="feedback_sources" 
                      checked={selectedSections.feedback_sources}
                      onCheckedChange={(checked) => handleSectionChange('feedback_sources', checked)}
                    />
                    <label
                      htmlFor="feedback_sources"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      Feedback Sources
                    </label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="product_feedback" 
                      checked={selectedSections.product_feedback}
                      onCheckedChange={(checked) => handleSectionChange('product_feedback', checked)}
                    />
                    <label
                      htmlFor="product_feedback"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      Product Feedback
                    </label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="detailed_feedback" 
                      checked={selectedSections.detailed_feedback}
                      onCheckedChange={(checked) => handleSectionChange('detailed_feedback', checked)}
                    />
                    <label
                      htmlFor="detailed_feedback"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      Detailed Feedback
                    </label>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button variant="outline" onClick={() => {
                // Reset form to defaults
                setTimeFilter("custom");
                setDateRange({
                  from: new Date(2024, 0, 1),
                  to: new Date(2024, 5, 30),
                });
                
                // Reset the checkboxes to checked
                setSelectedSections({
                  executive_summary: true,
                  sentiment_analysis: true,
                  feedback_sources: true,
                  product_feedback: true,
                  detailed_feedback: true
                });
              }}>Reset</Button>
              <Button onClick={handleGenerateReport} disabled={isGenerating}>
                {isGenerating ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Download className="mr-2 h-4 w-4" />
                    Generate Report
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>

          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Report Preview</CardTitle>
              <CardDescription>Preview your report before downloading</CardDescription>
              <div className="flex items-center justify-end space-x-2">
                <Button 
                  variant="default" 
                  onClick={handleGenerateReport} 
                  disabled={isGenerating}
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Download className="mr-2 h-4 w-4" />
                      Download Report
                    </>
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent className={"h-full"}>
              <Tabs defaultValue="preview">
                <TabsList className="mb-4">
                  <TabsTrigger value="preview">Preview</TabsTrigger>
                </TabsList>
                <TabsContent value="preview" className="space-y-4">
                  <div className="border rounded-lg p-6 space-y-2">
                    <h2 className="text-2xl font-bold">Comprehensive Report</h2>
                    <div className="text-sm text-muted-foreground">
                      Date Range: {dateRange.from ? dateRange.from.toLocaleDateString('en-US', {year: 'numeric', month: 'long', day: 'numeric'}) : ''} to {dateRange.to ? dateRange.to.toLocaleDateString('en-US', {year: 'numeric', month: 'long', day: 'numeric'}) : ''}
                    </div>
                    <div className="pt-4">
                      <p>This report includes the following sections:</p>
                      <ul className="list-disc list-inside space-y-1 pt-2">
                        {selectedSections.executive_summary && <li>Executive Summary</li>}
                        {selectedSections.sentiment_analysis && <li>Sentiment Analysis</li>}
                        {selectedSections.feedback_sources && <li>Feedback Sources</li>}
                        {selectedSections.product_feedback && <li>Product Feedback</li>}
                        {selectedSections.detailed_feedback && <li>Detailed Feedback</li>}
                      </ul>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

