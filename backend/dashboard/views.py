# views.py
from django.db.models.functions import ExtractYear, ExtractMonth, TruncMonth
from rest_framework import generics
from django.db.models import Count, Q, FloatField, ExpressionWrapper, F
from datetime import datetime, timedelta
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from reviews.models import Review
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import ReviewSerializer
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework import status
import io
from reportlab.pdfgen import canvas
from django.db.models import Count, Case, When
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
import json
from .gemini_service import generate_analysis


class TimeRangeMixin:
    def __init__(self):
        self.kwargs = None

    def get_time_constraints(self):
        time_range = self.kwargs.get('time_range', 'ALL')
        end_date = datetime.now()
        if time_range == '7D':
            start_date = end_date - timedelta(days=7)
        elif time_range == '14D':
            start_date = end_date - timedelta(days=14)
        elif time_range == '4W':
            start_date = end_date - timedelta(weeks=4)
        elif time_range == '3M':
            start_date = end_date - timedelta(days=3 * 30)
        elif time_range == '6M':
            start_date = end_date - timedelta(days=6 * 30)
        elif time_range == '12M':
            start_date = end_date - timedelta(days=365)
        else:  # Custom or ALL
            start_date = datetime.min

        return {'date__range': (start_date, end_date)}

class ReviewStatsView(generics.RetrieveAPIView, TimeRangeMixin):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        self.kwargs = request.query_params
        time_constraints = self.get_time_constraints()

        total_feedback = Review.objects.filter(**time_constraints).count()

        top_source = (Review.objects.filter(**time_constraints)
                     .values('source')
                     .annotate(count=Count('id'))
                     .order_by('-count')
                     .first())

        sentiment_counts = (Review.objects.filter(**time_constraints)
                          .values('sentiment')
                          .annotate(count=Count('id')))

        sentiment_stats = {s['sentiment']: s['count'] for s in sentiment_counts}
        highest_sentiment = max(sentiment_stats, key=sentiment_stats.get) if sentiment_stats else None

        response_data = {
            "total_feedback": total_feedback,
            "top_source": f"{top_source['source']} ({top_source['count']})" if top_source else "N/A",
            "most_common_sentiment": highest_sentiment or "N/A",
        }

        return Response(response_data)


class LastSixMonthsStatsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, time, *args, **kwargs):  # Changed to get and added time parameter
        end_date = datetime.now()
        start_date = end_date - timedelta(days=6 * 31)  # Roughly 6 months

        # Filter reviews for the last 6 months
        last_six_months_reviews = Review.objects.filter(date__gte=start_date, date__lte=end_date)

        # Aggregate data by month
        month_sentiment_counts = last_six_months_reviews.annotate(
            year=ExtractYear('date'),
            month=ExtractMonth('date')
        ).values('year', 'month', 'sentiment').annotate(count=Count('id')).order_by('year', 'month')

        # Organize data into a dictionary by year, month, and sentiment
        months_data = {}
        for item in month_sentiment_counts:
            year = item['year']
            month = item['month']
            sentiment = item['sentiment'] # Convert to lowercase to match frontend
            count = item['count']

            key = f"{year}-{month:02d}"  # Format as YYYY-MM for consistency
            if key not in months_data:
                months_data[key] = {'positive': 0, 'negative': 0, 'neutral': 0}

            months_data[key][sentiment] = count

        # Convert to list with month names
        response_data = []
        month_names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]

        # Get the last 6 months worth of data
        current_date = end_date
        for i in range(6):
            year = current_date.year
            month = current_date.month
            key = f"{year}-{month:02d}"
            month_name = month_names[month - 1]

            data = months_data.get(key, {'positive': 0, 'negative': 0, 'neutral': 0})
            response_data.insert(0, {  # Insert at beginning to get chronological order
                'month': month_name,
                'positive': data['positive'],
                'negative': data['negative'],
                'neutral': data['neutral'],
            })
            # Move to previous month
            current_date = current_date.replace(day=1) - timedelta(days=1)

        return Response(response_data)


class TrendingTopicsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Last 30 days

        # Fetch data for trending topics and their sentiments
        topics_data = (Review.objects.filter(date__gte=start_date, date__lte=end_date)
                       .values('category')
                       .annotate(
            mentions=Count('id'),
            negative_sentiment=Count('id', filter=Q(sentiment='negative')),
            positive_sentiment=Count('id', filter=Q(sentiment='positive')),
            neutral_sentiment=Count('id', filter=Q(sentiment='neutral'))
        )
                       .order_by('-mentions')[:5])

        # Fetch data for trend direction
        trends = Review.objects.filter(date__gte=start_date - timedelta(days=60), date__lte=end_date)

        # Calculate trend direction for each topic
        trend_data = {}
        for topic in topics_data:
            last_month_mentions = trends.filter(category=topic['category'], date__gte=start_date - timedelta(days=30),
                                                date__lte=start_date).count()
            this_month_mentions = topic['mentions']

            if topic['mentions'] > last_month_mentions + 5:  # Arbitrary threshold for 'up' trend
                trend_direction = "↑ Trending up"
            elif topic['mentions'] < last_month_mentions - 5:
                trend_direction = "↓ Trending down"
            else:
                trend_direction = "→ Stable"

            topic['trend_direction'] = trend_direction

            high_sentiment = max('negative_sentiment', 'positive_sentiment', key=topic.get)
            topic['sentiment'] = high_sentiment.split('_')[0]

            topic['last_30_days_mentions'] = topic['mentions']
            del topic['mentions'], topic['negative_sentiment'], topic['positive_sentiment'], topic['neutral_sentiment']

        return Response(topics_data)


class RecentFeedbackView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Review.objects.filter().order_by('-date')[:15]  # Fetch the last 15 reviews

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FeedbackSourcesView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, time, *args, **kwargs):
        end_date = datetime.now()

        # Determine time range based on the 'time' parameter
        if time == '7D':
            start_date = end_date - timedelta(days=7)
        elif time == '14D':
            start_date = end_date - timedelta(days=14)
        elif time == '4W':
            start_date = end_date - timedelta(weeks=4)
        elif time == '3M':
            start_date = end_date - timedelta(days=3 * 30)
        elif time == '6M':
            start_date = end_date - timedelta(days=6 * 30)
        elif time == '12M':
            start_date = end_date - timedelta(days=365)
        else:  # ALL or custom
            start_date = datetime.min

        # Fetch total counts by source
        source_counts = (Review.objects.filter(date__gte=start_date, date__lte=end_date)
                         .values('source')
                         .annotate(count=Count('id'))
                         .order_by('-count'))

        # Fetch data over time (last 6 months for detailed view)
        six_months_ago = end_date - timedelta(days=6 * 30)
        sources_over_time = (Review.objects.filter(date__gte=six_months_ago, date__lte=end_date)
                             .annotate(
            year=ExtractYear('date'),
            month=ExtractMonth('date')
        )
                             .values('year', 'month', 'source')
                             .annotate(count=Count('id'))
                             .order_by('year', 'month'))

        # Organize sources over time data
        months_data = {}
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        for item in sources_over_time:
            key = f"{month_names[item['month'] - 1]} {item['year']}"
            if key not in months_data:
                months_data[key] = {}
            months_data[key][item['source']] = item['count']

        # Format over-time data for the last 6 months
        over_time_data = []
        current_date = end_date
        for _ in range(6):
            month_name = month_names[current_date.month - 1]
            key = f"{month_name} {current_date.year}"
            month_data = months_data.get(key, {})
            over_time_data.insert(0, {
                'month': month_name,
                'Playstore': month_data.get('Playstore', 0),
                'Reddit': month_data.get('Reddit', 0),
                'X': month_data.get('X', 0),
                'AppStore': month_data.get('AppStore', 0),
                'Trust Pilot': month_data.get('Trust Pilot', 0),
            })
            current_date = current_date.replace(day=1) - timedelta(days=1)

        # Format response
        response_data = {
            'sources': [{'source': item['source'], 'count': item['count']} for item in source_counts],
            'sources_over_time': over_time_data
        }

        return Response(response_data)

class SentimentDistributionView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        total_reviews = Review.objects.count()
        sentiments = Review.objects.values('sentiment').annotate(count=Count('id'))

        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for item in sentiments:
            sentiment_counts[item['sentiment']] = item['count']

        response_data = {
            "overall_distribution": {
                "positive": round((sentiment_counts['positive'] / total_reviews) * 100, 2),
                "negative": round((sentiment_counts['negative'] / total_reviews) * 100, 2),
                "neutral": round((sentiment_counts['neutral'] / total_reviews) * 100, 2)
            }
        }

        return Response(response_data)

class SentimentTrendsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=6 * 31)  # More accurate for 6 months

        monthly_sentiments = (Review.objects
                              .filter(date__gte=start_date, date__lte=end_date)
                              .annotate(month=TruncMonth('date'))
                              .values('month', 'sentiment')
                              .annotate(count=Count('id'))
                              .order_by('month'))

        data = {}
        for month_item in monthly_sentiments:
            month = month_item['month'].strftime('%b')
            if month not in data:
                data[month] = {'positive': 0, 'negative': 0, 'neutral': 0}
            data[month][month_item['sentiment']] = month_item['count']

        response_data = {
            "trends": [
                {"month": month, "positive": item['positive'], "negative": item['negative'], "neutral": item['neutral']}
                for month, item in data.items()
            ]
        }

        return Response(response_data)


class SentimentBySourceView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        predefined_sources = ['googleplay', 'reddit', 'twitter', 'appstore', 'trustpilot']

        # Aggregate counts per source with sentiment breakdown
        aggregated = Review.objects.filter(source__in=predefined_sources).values('source').annotate(
            positive_count=Count(Case(When(sentiment='positive', then=1))),
            negative_count=Count(Case(When(sentiment='negative', then=1))),
            neutral_count=Count(Case(When(sentiment='neutral', then=1))),
            total=Count('id')
        )

        # Build the response data
        response_data = {"sources": {}}
        for data in aggregated:
            source = data['source']
            total = data['total'] if data['total'] > 0 else 1  # avoid division by zero
            response_data["sources"][source] = {
                "positive": round((data['positive_count'] * 100.0) / total, 2),
                "negative": round((data['negative_count'] * 100.0) / total, 2),
                "neutral": round((data['neutral_count'] * 100.0) / total, 2)
            }

        # Ensure that all predefined sources are in the response
        for source in predefined_sources:
            if source not in response_data["sources"]:
                response_data["sources"][source] = {"positive": 0, "negative": 0, "neutral": 0}

        return Response(response_data)


class ProductFeedbackCategoriesView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        categories = Review.objects.values('category').annotate(
            positive=Count('id', filter=Q(sentiment='positive')),
            negative=Count('id', filter=Q(sentiment='negative'))
        )

        response_data = [
            {"category": item['category'], "positive": item['positive'], "negative": item['negative']}
            for item in categories
        ]

        return Response(response_data)

class TopFeedbackTopicsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        topics = Review.objects.values('category').annotate(
            count=Count('id'),
            sentiment=F('sentiment')
        ).order_by('-count')[:12]

        response_data = [
            {"name": item['category'], "count": item['count'], "sentiment": item['sentiment']}
            for item in topics
        ]

        return Response(response_data)

class FeatureSpecificFeedbackView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        features = Review.objects.values('category').annotate(
            positive=Count('id', filter=Q(sentiment='positive')),
            negative=Count('id', filter=Q(sentiment='negative'))
        )

        response_data = [
            {"name": item['category'], "positive": item['positive'], "negative": item['negative']}
            for item in features
        ]

        return Response(response_data)

class FeedbackSourcesDetailedView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        end_date = datetime.now()

        # Fetch total counts by source
        source_counts = (Review.objects.filter(date__lte=end_date)
                         .values('source')
                         .annotate(count=Count('id'))
                         .order_by('-count'))

        # Fetch data over time (last 6 months for detailed view)
        six_months_ago = end_date - timedelta(days=6 * 30)
        sources_over_time = (Review.objects.filter(date__gte=six_months_ago, date__lte=end_date)
                             .annotate(
            year=ExtractYear('date'),
            month=ExtractMonth('date')
        )
                             .values('year', 'month', 'source')
                             .annotate(count=Count('id'))
                             .order_by('year', 'month'))

        # Organize sources over time data
        months_data = {}
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        for item in sources_over_time:
            key = f"{month_names[item['month'] - 1]} {item['year']}"
            if key not in months_data:
                months_data[key] = {}
            months_data[key][item['source']] = item['count']

        # Format over-time data for the last 6 months
        over_time_data = []
        current_date = end_date
        for _ in range(6):
            month_name = month_names[current_date.month - 1]
            key = f"{month_name} {current_date.year}"
            month_data = months_data.get(key, {})
            over_time_data.insert(0, {
                'month': month_name,
                'Playstore': month_data.get('Playstore', 0),
                'Reddit': month_data.get('Reddit', 0),
                'X': month_data.get('X', 0),
                'AppStore': month_data.get('AppStore', 0),
                'Trust Pilot': month_data.get('Trust Pilot', 0),
            })
            current_date = current_date.replace(day=1) - timedelta(days=1)

        # Format response
        response_data = {
            'sources': [{'source': item['source'], 'count': item['count']} for item in source_counts],
            'sources_over_time': over_time_data
        }

        return Response(response_data)

class FeedbackPagination(PageNumberPagination):
    page_size = 100  # Number of reviews per page
    page_size_query_param = 'page_size'
    max_page_size = 1000

class FeedbackDetailsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    pagination_class = FeedbackPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Review.objects.filter(user_data__user=user)

        # Apply filters
        search = self.request.query_params.get('search', '')
        source = self.request.query_params.get('source', '')
        sentiment = self.request.query_params.get('sentiment', '')
        category = self.request.query_params.get('category', '')
        print(f"Filters: search={search}, source={source}, sentiment={sentiment}, category={category}")

        if search:
            queryset = queryset.filter(Q(review__icontains=search) | Q(title__icontains=search))

        # Only apply filters if not "all"
        if source and source != "all":
            queryset = queryset.filter(source=source)
        if sentiment and sentiment != "all":
            queryset = queryset.filter(sentiment=sentiment)
        if category and category != "all":
            queryset = queryset.filter(category=category)

        return queryset.order_by('-date')


class GenerateReportView(APIView):
    def _get_date_filter(self, time_filter, date_range=None):
        """
        Convert time filter to a dictionary suitable for database filtering
        """
        from django.utils import timezone
        import datetime
        
        today = timezone.now()
        date_filter = {'date__isnull': False}
        
        if time_filter == 'daily':
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            date_filter = {'date__gte': today_start}
        elif time_filter == 'weekly':
            week_ago = today - datetime.timedelta(days=7)
            date_filter = {'date__gte': week_ago}
        elif time_filter == 'monthly':
            month_ago = today - datetime.timedelta(days=30)
            date_filter = {'date__gte': month_ago}
        elif time_filter == 'quarterly':
            quarter_ago = today - datetime.timedelta(days=90)
            date_filter = {'date__gte': quarter_ago}
        elif time_filter == 'custom' and date_range:
            from_date = date_range.get('from')
            to_date = date_range.get('to')
            if from_date:
                try:
                    from_datetime = datetime.datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                    date_filter['date__gte'] = from_datetime
                except (ValueError, TypeError):
                    pass  
            if to_date:
                try:
                    to_datetime = datetime.datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                    to_datetime = to_datetime.replace(hour=23, minute=59, second=59)
                    date_filter['date__lte'] = to_datetime
                except (ValueError, TypeError):
                    pass
        return date_filter

    def post(self, request, *args, **kwargs):
        try:
            # Extract parameters
            report_type = request.data.get('reportType', 'comprehensive')
            time_filter = request.data.get('timeFilter', 'default')
            date_range = request.data.get('dateRange', {})
            format_type = request.data.get('format', 'pdf')
            sections = request.data.get('sections', [])
            
            # Create a file-like buffer to receive PDF data
            buffer = io.BytesIO()
            
            # Create the PDF object using the buffer as its "file"
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Add title
            title_style = styles['Heading1']
            title = f"{report_type.title()} Report"
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
            # Add date range - Use formatted dates if available, otherwise use ISO dates
            date_from = date_range.get('fromFormatted', date_range.get('from', ''))
            date_to = date_range.get('toFormatted', date_range.get('to', ''))
            
            if date_from and date_to:
                date_text = f"Date Range: {date_from} to {date_to}"
                story.append(Paragraph(date_text, styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Ensure sections is a list
            if isinstance(sections, str):
                sections = [sections]
                
            # Log sections for debugging
            print(f"Processing report with sections: {sections}")
                
            # Add sections based on selection with date_range
            if 'executive_summary' in sections:
                self._add_executive_summary(story, styles, time_filter, date_range=None)
            
            if 'sentiment_analysis' in sections:
                self._add_sentiment_analysis(story, styles, time_filter, date_range=None)
            
            if 'feedback_sources' in sections:
                self._add_feedback_sources(story, styles, time_filter, date_range=None)
            
            if 'product_feedback' in sections:
                self._add_product_feedback(story, styles, time_filter, date_range=None)
            
            if 'detailed_feedback' in sections:
                self._add_detailed_feedback(story, styles, time_filter, date_range=None)
            
            # Build the PDF
            doc.build(story)
            buffer.seek(0)
            
            # Return the PDF file
            return FileResponse(
                buffer, 
                as_attachment=True,
                filename=f"{report_type}_report_{datetime.now().strftime('%Y-%m-%d')}.pdf"
            )
            
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _add_executive_summary(self, story, styles, time_filter, date_range=None):
        from django.db.models import Avg, Count
        from reviews.models import Review
        
        # Get date filter based on time_filter
        date_filter = self._get_date_filter(time_filter, date_range)
        
        # Apply date filter to all queries
        total_reviews = Review.objects.filter(**date_filter).count()
        
        # For sentiment analysis with date filtering
        sentiments = Review.objects.filter(**date_filter).values('sentiment').annotate(count=Count('id'))
        
        # Calculate positive percentage with null handling
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0, 'unknown': 0}
        for item in sentiments:
            # Handle None values
            sentiment_key = item['sentiment'] if item['sentiment'] is not None else 'unknown'
            sentiment_counts[sentiment_key] = item.get('count', 0)
        
        # Calculate percentages safely
        positive_percentage = 0
        negative_percentage = 0
        neutral_percentage = 0
        unknown_percentage = 0
        
        if total_reviews > 0:
            positive_percentage = round((sentiment_counts['positive'] / total_reviews) * 100, 2)
            negative_percentage = round((sentiment_counts['negative'] / total_reviews) * 100, 2)
            neutral_percentage = round((sentiment_counts['neutral'] / total_reviews) * 100, 2)
            unknown_percentage = round((sentiment_counts['unknown'] / total_reviews) * 100, 2)
        
        # Add title
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Add statistics as paragraphs
        story.append(Paragraph(f"Total Feedback: {total_reviews}", styles['Normal']))
        story.append(Paragraph(f"Positive Sentiment: {positive_percentage}%", styles['Normal']))
        story.append(Paragraph(f"Negative Sentiment: {negative_percentage}%", styles['Normal']))
        story.append(Paragraph(f"Neutral Sentiment: {neutral_percentage}%", styles['Normal']))
        if unknown_percentage > 0:
            story.append(Paragraph(f"Unknown Sentiment: {unknown_percentage}%", styles['Normal']))
        story.append(Spacer(1, 12))
    
    def _add_sentiment_analysis(self, story, styles, time_filter, date_range=None):
        from django.db.models import Count
        from reviews.models import Review
        
        # Get date filter and apply to all queries
        date_filter = self._get_date_filter(time_filter, date_range)
        
        total_reviews = Review.objects.filter(**date_filter).count()
        sentiments = Review.objects.filter(**date_filter).values('sentiment').annotate(count=Count('id'))
        
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0, 'unknown': 0}
        for item in sentiments:
            # Handle None values
            sentiment_key = item['sentiment'] if item['sentiment'] is not None else 'unknown'
            sentiment_counts[sentiment_key] = item.get('count', 0)
            
        # Add title and content
        story.append(Paragraph("Sentiment Analysis", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Create a table for sentiment distribution
        data = [["Sentiment", "Count", "Percentage"]]
        for sentiment, count in sentiment_counts.items():
            percentage = round((count / total_reviews) * 100, 2) if total_reviews > 0 else 0
            # Safe capitalize with null check
            sentiment_display = sentiment.capitalize() if sentiment else "Unknown"
            data.append([sentiment_display, str(count), f"{percentage}%"])
        
        # Add table
        table = Table(data, colWidths=[150, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 12))
    
    def _add_feedback_sources(self, story, styles, time_filter, date_range=None):
        from django.db.models import Count
        from reviews.models import Review
        
        # Get date filter and apply to all queries
        date_filter = self._get_date_filter(time_filter, date_range)
        
        # Add title
        story.append(Paragraph("Feedback Sources", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Fetch sources with null handling
        sources = Review.objects.filter(**date_filter).values('source').annotate(count=Count('id'))
        
        # Add information about sources with null checks
        if not sources:
            story.append(Paragraph("No source data available", styles['Normal']))
        else:
            for source in sources:
                source_name = source['source'] if source['source'] else "Unknown source"
                story.append(Paragraph(f"{source_name}: {source['count']} reviews", styles['Normal']))
        
        story.append(Spacer(1, 12))
    
    def _add_product_feedback(self, story, styles, time_filter, date_range=None):
        from django.db.models import Count
        from reviews.models import Review
        
        # Get date filter and apply to all queries
        date_filter = self._get_date_filter(time_filter, date_range)
        
        # Add title
        story.append(Paragraph("Product Feedback", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Get top product categories
        categories = Review.objects.filter(**date_filter).values('category').annotate(count=Count('id')).order_by('-count')[:5]
        
        # Add product category information with null checks
        story.append(Paragraph("Top Product Categories:", styles['Heading3']))
        if not categories:
            story.append(Paragraph("No category data available", styles['Normal']))
        else:
            for cat in categories:
                category_name = cat['category'] if cat['category'] else "Uncategorized"
                story.append(Paragraph(f"{category_name}: {cat['count']} mentions", styles['Normal']))
        
        story.append(Spacer(1, 12))
    
    def _add_detailed_feedback(self, story, styles, time_filter, date_range=None):
        from reviews.models import Review
        
        # Get date filter and apply to all queries
        date_filter = self._get_date_filter(time_filter, date_range)
        
        # Add title
        story.append(Paragraph("Detailed Feedback", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Get recent reviews with detailed comments
        reviews = Review.objects.filter(**date_filter).order_by('-date')[:10]
        
        # Add detailed reviews with null checks
        for idx, review in enumerate(reviews, 1):
            story.append(Paragraph(f"Review #{idx}", styles['Heading3']))
            
            # Safe display with null checks
            sentiment = review.sentiment.capitalize() if review.sentiment else "Unknown"
            category = review.category if review.category else "Uncategorized"
            source = review.source if review.source else "Unknown source"
            
            story.append(Paragraph(f"Sentiment: {sentiment}", styles['Normal']))
            story.append(Paragraph(f"Category: {category}", styles['Normal']))
            story.append(Paragraph(f"Source: {source}", styles['Normal']))
            
            # Only include text if it exists (could be in review or comments field)
            if hasattr(review, 'review') and review.review:
                story.append(Paragraph(f"Feedback: {review.review}", styles['Normal']))
            elif hasattr(review, 'comments') and review.comments:
                story.append(Paragraph(f"Feedback: {review.comments}", styles['Normal']))
                
            story.append(Spacer(1, 12))

    # def _get_date_filter(self, time_filter):
    #     from datetime import datetime, timedelta
    #     from django.db.models import Q
        
    #     now = datetime.now()
        
    #     if time_filter == 'week':
    #         start_date = now - timedelta(days=7)
    #         return Q(date__gte=start_date)  # Using 'date' field from Review model
    #     elif time_filter == 'month':
    #         start_date = now - timedelta(days=30)
    #         return Q(date__gte=start_date)
    #     elif time_filter == 'quarter':
    #         start_date = now - timedelta(days=90)
    #         return Q(date__gte=start_date)
    #     elif time_filter == 'year':
    #         start_date = now - timedelta(days=365)
    #         return Q(date__gte=start_date)
    #     elif time_filter == 'custom' and hasattr(self, 'request') and 'dateRange' in self.request.data:
    #         from_date = self.request.data['dateRange']['from']
    #         to_date = self.request.data['dateRange']['to']
    #         return Q(date__gte=from_date, date__lte=to_date)
    #     else:
    #         # Default to all time
    #         return Q()


class TrendAnalysisView(APIView):
    # For testing, we can comment out the authentication requirement
    # permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Extract request data
            category = request.data.get('category')
            date_from = request.data.get('dateRange', {}).get('from')
            date_to = request.data.get('dateRange', {}).get('to')
            time_preset = request.data.get('timePreset')
            
            # If time preset is provided, calculate date range
            if time_preset:
                date_to = datetime.now()
                if time_preset == 'daily':
                    date_from = date_to - timedelta(days=1)
                elif time_preset == 'weekly':
                    date_from = date_to - timedelta(days=7)
                elif time_preset == 'monthly':
                    date_from = date_to - timedelta(days=30)
                elif time_preset == 'quarterly':
                    date_from = date_to - timedelta(days=90)
                else:
                    return Response(
                        {"error": f"Invalid time preset: {time_preset}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Format dates for the query
                date_from = date_from.strftime('%Y-%m-%d')
                date_to = date_to.strftime('%Y-%m-%d')
            
            if not category or (not time_preset and (not date_from or not date_to)):
                return Response(
                    {"error": "Missing required parameters: category and either timePreset or dateRange"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # Convert string dates to datetime objects
                from_date = datetime.strptime(date_from, "%Y-%m-%d")
                to_date = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)  # Include the end date
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Please use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Query database for ALL reviews in the date range for the selected category
            reviews = Review.objects.filter(
                category=category,
                date__gte=from_date,
                date__lte=to_date
            ).order_by('-date')
            
            # Get total count for metadata
            total_count = reviews.count()
            
            # Format reviews for analysis - get all of them
            review_texts = [review.review for review in reviews]
            
            if not review_texts:
                return Response(
                    {
                        "pros": [f"No reviews found for category '{category}' in the selected date range."],
                        "cons": ["Consider selecting a different date range or category."],
                        "positiveInsights": ["No data available"],
                        "negativeInsights": ["No data available"],
                        "summary": f"No reviews found for category '{category}' between {date_from} and {date_to}.",
                        "metadata": {
                            "reviewCount": 0,
                            "dateRange": {"from": date_from, "to": date_to},
                            "category": category
                        }
                    },
                    status=status.HTTP_200_OK
                )
                
            # Generate analysis
            analysis_result = generate_analysis(review_texts, category, date_from)
            
            # Add metadata to the response
            analysis_result["metadata"] = {
                "reviewCount": total_count,
                "dateRange": {"from": date_from, "to": date_to},
                "category": category
            }
            
            return Response(analysis_result)
            
        except Exception as e:
            import traceback
            print(f"Error in trend analysis: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {
                    "error": str(e),
                    "pros": ["Analysis failed. Please try again later."],
                    "cons": ["If the problem persists, contact support."],
                    "positiveInsights": ["Analysis error"],
                    "negativeInsights": ["Analysis error"],
                    "summary": "An error occurred during analysis."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

