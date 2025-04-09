"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, Filter, MessageSquare, Bookmark, Flag, ChevronLeft, ChevronRight } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { getFeedbackDetails } from "@/pages/Dashboard/api.ts";

interface FeedbackItem {
  id: number
  review_id: string
  date: string
  rating: number | null
  source: string
  review: string
  title: string | null
  username: string | null
  url: string
  category: string | null
  sub_category: string | null
  sentiment: "positive" | "negative" | "neutral" | null
  particular_issue: string | null
  summary: string | null
}

interface PaginatedResponse {
  count: number
  next: string | null
  previous: string | null
  results: FeedbackItem[]
}

export function FeedbackDetails() {
  const [feedbackData, setFeedbackData] = useState<FeedbackItem[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedSource, setSelectedSource] = useState("all")
  const [selectedSentiment, setSelectedSentiment] = useState("all")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [selectedFeedback, setSelectedFeedback] = useState<FeedbackItem | null>(null)
  const [notes, setNotes] = useState<Record<string, string>>({})
  const [important, setImportant] = useState<Record<string, boolean>>({})
  const [loading, setLoading] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalCount, setTotalCount] = useState(0)

  useEffect(() => {
    fetchFeedbackData(1)
  }, [searchTerm, selectedSource, selectedSentiment, selectedCategory])

  const fetchFeedbackData = async (page: number) => {
    setLoading(true)
    try {
      const response = await getFeedbackDetails(searchTerm, selectedSource, selectedSentiment, selectedCategory, page);
      setFeedbackData(response.results)
      setTotalCount(response.count)
      setTotalPages(Math.ceil(response.count / 100))
      setCurrentPage(page)
    } catch (error) {
      console.error('Error fetching feedback data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      fetchFeedbackData(newPage)
    }
  }

  const toggleImportant = (reviewId: string) => {
    setImportant((prev) => ({
      ...prev,
      [reviewId]: !prev[reviewId],
    }))
  }

  const updateNotes = (reviewId: string, note: string) => {
    setNotes((prev) => ({
      ...prev,
      [reviewId]: note,
    }))
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Feedback Details</CardTitle>
        <CardDescription>View and analyze individual feedback entries</CardDescription>
        <div className="flex flex-col space-y-4 md:flex-row md:space-y-0 md:space-x-4 mt-4">
          <div className="flex w-full items-center space-x-2">
            <Input
              placeholder="Search feedback..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1"
            />
            <Button type="submit" size="icon" onClick={() => fetchFeedbackData(1)}>
              <Search className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex space-x-2">
            <Select value={selectedSource} onValueChange={setSelectedSource}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Source" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sources</SelectItem>
                <SelectItem value="googleplay">Playstore</SelectItem>
                <SelectItem value="reddit">Reddit</SelectItem>
                <SelectItem value="twitter">X</SelectItem>
                <SelectItem value="appstore">AppStore</SelectItem>
                <SelectItem value="trustpilot">Trust Pilot</SelectItem>
              </SelectContent>
            </Select>
            <Select value={selectedSentiment} onValueChange={setSelectedSentiment}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Sentiment" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sentiments</SelectItem>
                <SelectItem value="positive">Positive</SelectItem>
                <SelectItem value="negative">Negative</SelectItem>
                <SelectItem value="neutral">Neutral</SelectItem>
              </SelectContent>
            </Select>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>

                <SelectItem value="Ride Availability">Ride Availability</SelectItem>
                <SelectItem value="App Performance">App Performance</SelectItem>
                <SelectItem value="Bans & Restrictions">Bans & Restrictions</SelectItem>
                <SelectItem value="Company Policies">Company Policies</SelectItem>
                <SelectItem value="Customer Support">Customer Support</SelectItem>

                <SelectItem value="Discounts & Offers">Discounts & Offers</SelectItem>
                <SelectItem value="Driver Experience">Driver Experience</SelectItem>
                <SelectItem value="Payment & Transactions">Payment & Transactions</SelectItem>
                <SelectItem value="Pricing">Pricing</SelectItem>

                <SelectItem value="Ratings & Reviews">Ratings & Reviews</SelectItem>
                <SelectItem value="Regulations & Legal">Regulations & Legal</SelectItem>
                <SelectItem value="Ride Availability">Ride Availability</SelectItem>

                <SelectItem value="Security">Security</SelectItem>
                <SelectItem value="Sustainability & Environment">Sustainability & Environment</SelectItem>
                <SelectItem value="Trust & Safety">Trust & Safety</SelectItem>
                <SelectItem value="User Interface">User Interface</SelectItem>
                {/* Add categories dynamically based on your data */}
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" onClick={() => fetchFeedbackData(1)}>
              <Filter className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center py-8">Loading feedback data...</div>
        ) : feedbackData.length === 0 ? (
          <div className="flex justify-center py-8">No feedback found matching your criteria</div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Feedback</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Sentiment</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {feedbackData.map((item) => (
                  <TableRow key={item.review_id}>
                    <TableCell className="font-medium max-w-md truncate">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button
                            variant="link"
                            className="p-0 h-auto text-left justify-start"
                            onClick={() => setSelectedFeedback(item)}
                          >
                            {item.review.substring(0, 100)}
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="sm:max-w-[625px]">
                          <DialogHeader>
                            <DialogTitle>Feedback Details</DialogTitle>
                            <DialogDescription>View complete feedback and add notes</DialogDescription>
                          </DialogHeader>
                          <div className="grid gap-4 py-4">
                            <div className="flex items-center justify-between">
                              <Badge variant={item.sentiment === "positive" ? "default" : "destructive"}>
                                {item.sentiment}
                              </Badge>
                              <span className="text-sm text-muted-foreground">
                                {item.source} • {new Date(item.date).toLocaleDateString()}
                              </span>
                            </div>
                            <div className="border rounded-md p-4">{item.review}</div>
                            <div>
                              <h4 className="mb-2 text-sm font-medium">Add Notes</h4>
                              <Textarea
                                placeholder="Add your notes about this feedback..."
                                value={notes[item.review_id] || ""}
                                onChange={(e) => updateNotes(item.review_id, e.target.value)}
                              />
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </TableCell>
                    <TableCell>{item.source}</TableCell>
                    <TableCell>{new Date(item.date).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Badge variant={item.sentiment === "positive" ? "default" : "destructive"}>{item.sentiment}</Badge>
                    </TableCell>
                    <TableCell>{item.category}</TableCell>
                    <TableCell>
                      <div className="flex space-x-1">
                        <Button variant="ghost" size="icon" onClick={() => toggleImportant(item.review_id)}>
                          <Bookmark className={`h-4 w-4 ${important[item.review_id] ? "fill-current" : ""}`} />
                        </Button>
                        <Button variant="ghost" size="icon">
                          <MessageSquare className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon">
                          <Flag className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <div className="flex items-center justify-between mt-6">
              <div className="text-sm text-muted-foreground">
                Showing {(currentPage - 1) * 100 + 1} to {Math.min(currentPage * 100, totalCount)} of {totalCount} entries
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <div className="text-sm">
                  Page {currentPage} of {totalPages}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
