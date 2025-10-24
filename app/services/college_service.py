from app.models.college import College
from app.schemas.college import CollegeListPageResponse
from typing import Optional, List, Tuple
import re

class CollegeService:
    @staticmethod
    async def get_colleges(
        query: dict = {},
        sort_criteria: Optional[List[Tuple[str, int]]] = None,
        page: int = 1,
        page_size: int = 10
    ) -> CollegeListPageResponse:
        
        print(
            f"Query: {query}, Sort: {sort_criteria}, Page: {page}, Page Size: {page_size}"
        )
        # Sample colleges data
        all_colleges = [
            {
                "id": "1",
                "name": 'Indian Institute of Technology Delhi',
                "shortName": 'IIT Delhi',
                "location": 'New Delhi',
                "state": 'Delhi',
                "rating": 4.8,
                "reviews": 2453,
                "type": 'Public',
                "category": 'Engineering',
                "established": 1961,
                "fees": 250000,
                "placement": 2500000,
                "ranking": 2,
                "featured": True,
                "courses": 42,
                "students": 8000,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "2",
                "name": 'All India Institute of Medical Sciences',
                "shortName": 'AIIMS Delhi',
                "location": 'New Delhi',
                "state": 'Delhi',
                "rating": 4.9,
                "reviews": 1876,
                "type": 'Public',
                "category": 'Medical',
                "established": 1956,
                "fees": 150000,
                "placement": 3000000,
                "ranking": 1,
                "featured": True,
                "courses": 28,
                "students": 3000,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "3",
                "name": 'Indian Institute of Management Ahmedabad',
                "shortName": 'IIM Ahmedabad',
                "location": 'Ahmedabad',
                "state": 'Gujarat',
                "rating": 4.7,
                "reviews": 1234,
                "type": 'Public',
                "category": 'Management',
                "established": 1961,
                "fees": 2500000,
                "placement": 3500000,
                "ranking": 1,
                "featured": True,
                "courses": 15,
                "students": 1200,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "4",
                "name": 'Indian Institute of Science',
                "shortName": 'IISc Bangalore',
                "location": 'Bangalore',
                "state": 'Karnataka',
                "rating": 4.8,
                "reviews": 987,
                "type": 'Public',
                "category": 'Science & Research',
                "established": 1909,
                "fees": 200000,
                "placement": 2800000,
                "ranking": 1,
                "featured": True,
                "courses": 35,
                "students": 4500,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "5",
                "name": 'Delhi University',
                "shortName": 'DU',
                "location": 'New Delhi',
                "state": 'Delhi',
                "rating": 4.5,
                "reviews": 5432,
                "type": 'Public',
                "category": 'Arts & Science',
                "established": 1922,
                "fees": 50000,
                "placement": 800000,
                "ranking": 12,
                "featured": False,
                "courses": 180,
                "students": 400000,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "6",
                "name": 'Indian Institute of Technology Bombay',
                "shortName": 'IIT Bombay',
                "location": 'Mumbai',
                "state": 'Maharashtra',
                "rating": 4.8,
                "reviews": 2156,
                "type": 'Public',
                "category": 'Engineering',
                "established": 1958,
                "fees": 250000,
                "placement": 2700000,
                "ranking": 3,
                "featured": True,
                "courses": 45,
                "students": 9000,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "7",
                "name": 'Jawaharlal Nehru University',
                "shortName": 'JNU',
                "location": 'New Delhi',
                "state": 'Delhi',
                "rating": 4.6,
                "reviews": 1543,
                "type": 'Public',
                "category": 'Arts & Science',
                "established": 1969,
                "fees": 20000,
                "placement": 600000,
                "ranking": 8,
                "featured": False,
                "courses": 75,
                "students": 8500,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "8",
                "name": 'Indian Institute of Technology Madras',
                "shortName": 'IIT Madras',
                "location": 'Chennai',
                "state": 'Tamil Nadu',
                "rating": 4.9,
                "reviews": 2891,
                "type": 'Public',
                "category": 'Engineering',
                "established": 1959,
                "fees": 250000,
                "placement": 2800000,
                "ranking": 1,
                "featured": True,
                "courses": 50,
                "students": 10000,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "9",
                "name": 'National Law School of India University',
                "shortName": 'NLSIU Bangalore',
                "location": 'Bangalore',
                "state": 'Karnataka',
                "rating": 4.7,
                "reviews": 876,
                "type": 'Public',
                "category": 'Law',
                "established": 1987,
                "fees": 400000,
                "placement": 2000000,
                "ranking": 1,
                "featured": True,
                "courses": 8,
                "students": 800,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "10",
                "name": 'Banaras Hindu University',
                "shortName": 'BHU',
                "location": 'Varanasi',
                "state": 'Uttar Pradesh',
                "rating": 4.4,
                "reviews": 3421,
                "type": 'Public',
                "category": 'Arts & Science',
                "established": 1916,
                "fees": 60000,
                "placement": 700000,
                "ranking": 15,
                "featured": False,
                "courses": 140,
                "students": 30000,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "11",
                "name": 'BITS Pilani',
                "shortName": 'BITS Pilani',
                "location": 'Pilani',
                "state": 'Rajasthan',
                "rating": 4.6,
                "reviews": 1987,
                "type": 'Private',
                "category": 'Engineering',
                "established": 1964,
                "fees": 450000,
                "placement": 2300000,
                "ranking": 5,
                "featured": True,
                "courses": 38,
                "students": 4500,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "12",
                "name": 'Manipal Academy of Higher Education',
                "shortName": 'MAHE',
                "location": 'Manipal',
                "state": 'Karnataka',
                "rating": 4.3,
                "reviews": 2134,
                "type": 'Private',
                "category": 'Medical',
                "established": 1953,
                "fees": 1800000,
                "placement": 1500000,
                "ranking": 10,
                "featured": False,
                "courses": 65,
                "students": 28000,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "13",
                "name": 'Vellore Institute of Technology',
                "shortName": 'VIT Vellore',
                "location": 'Vellore',
                "state": 'Tamil Nadu',
                "rating": 4.4,
                "reviews": 3567,
                "type": 'Private',
                "category": 'Engineering',
                "established": 1984,
                "fees": 175000,
                "placement": 1200000,
                "ranking": 11,
                "featured": False,
                "courses": 52,
                "students": 35000,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "14",
                "name": 'Indian Statistical Institute',
                "shortName": 'ISI Kolkata',
                "location": 'Kolkata',
                "state": 'West Bengal',
                "rating": 4.7,
                "reviews": 654,
                "type": 'Public',
                "category": 'Science & Research',
                "established": 1931,
                "fees": 100000,
                "placement": 2400000,
                "ranking": 3,
                "featured": True,
                "courses": 12,
                "students": 900,
                "image": '/api/placeholder/400/300'
            },
            {
                "id": "15",
                "name": 'Amity University',
                "shortName": 'Amity Noida',
                "location": 'Noida',
                "state": 'Uttar Pradesh',
                "rating": 4.2,
                "reviews": 4321,
                "type": 'Private',
                "category": 'Arts & Science',
                "established": 2005,
                "fees": 200000,
                "placement": 600000,
                "ranking": 20,
                "featured": False,
                "courses": 95,
                "students": 45000,
                "image": '/api/placeholder/400/300'
            }
        ]

        # Apply filters from query
        filtered_colleges = all_colleges.copy()

        # Name search filter (case-insensitive)
        if 'name' in query and '$regex' in query['name']:
            search_pattern = query['name']['$regex']
            filtered_colleges = [
                c for c in filtered_colleges
                if re.search(search_pattern, c['name'], re.IGNORECASE)
            ]

        # State filter
        if 'state' in query:
            filtered_colleges = [
                c for c in filtered_colleges
                if c['state'] == query['state']
            ]

        # Type filter
        if 'type' in query:
            filtered_colleges = [
                c for c in filtered_colleges
                if c['type'] == query['type']
            ]

        # Category filter
        if 'category' in query:
            filtered_colleges = [
                c for c in filtered_colleges
                if c['category'] == query['category']
            ]

        # Apply sorting
        if sort_criteria:
            sort_field, sort_order = sort_criteria[0]
            reverse = sort_order == -1
            filtered_colleges = sorted(
                filtered_colleges,
                key=lambda x: x.get(sort_field, 0),
                reverse=reverse
            )

        # Calculate pagination
        total = len(filtered_colleges)
        total_pages = (total + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_colleges = filtered_colleges[start_idx:end_idx]

        # Convert fees and placement back to string format for display
        for college in paginated_colleges:
            print(college['name'])
            college['fees'] = f"₹{college['fees'] / 100000:.1f} Lakhs"
            college['placement'] = f"₹{college['placement'] / 100000:.0f} LPA"

        return CollegeListPageResponse(
            colleges=paginated_colleges,
            total=total,
            page=page,
            size=page_size
        )
