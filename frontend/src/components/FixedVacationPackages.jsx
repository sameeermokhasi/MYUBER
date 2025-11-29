import { useState } from 'react';
import { MapPin, Calendar, Star } from 'lucide-react';
import { vacationService, vacationSchedulerService } from '../services/api';

const FIXED_PACKAGES = [
  {
    id: 1,
    name: "Gokarna Adventure Package",
    destination: "Gokarna, Karnataka",
    days: 3,
    nights: 2,
    price: 8500,
    images: [
      "https://images.unsplash.com/photo-1523880842382-9f8d8a0c1a5a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1561501930-6a605d0b7a9d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
    ],
    description: "Experience the spiritual and adventurous side of Gokarna with this 3-day package",
    itinerary: [
      {
        day: 1,
        schedule: [
          { time: "7:00 AM", activity: "Pickup from Hubli/Dharwad" },
          { time: "8:30 AM", activity: "Breakfast at local restaurant" },
          { time: "10:00 AM", activity: "Visit Mahabaleshwar Temple" },
          { time: "11:30 AM", activity: "Beach and water activities at Om Beach" },
          { time: "2:00 PM", activity: "Lunch at beachside restaurant" },
          { time: "4:00 PM", activity: "Visit hidden beaches (Kudle, Paradise, Half Moon)" },
          { time: "6:00 PM", activity: "Ride to Honnavar" },
          { time: "8:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 2,
        schedule: [
          { time: "6:00 AM", activity: "Breakfast and visit Murdeshwara Shiva Temple" },
          { time: "9:00 AM", activity: "Visit famous beach and water activities" },
          { time: "11:00 AM", activity: "Water sports (optional)" },
          { time: "1:00 PM", activity: "Lunch" },
          { time: "3:00 PM", activity: "Back to Honnavar" },
          { time: "5:00 PM", activity: "Honnavar backwaters boating" },
          { time: "7:00 PM", activity: "Tea and snacks" },
          { time: "9:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 3,
        schedule: [
          { time: "6:00 AM", activity: "Breakfast" },
          { time: "8:00 AM", activity: "Check-out and back to Hubli" },
          { time: "12:00 PM", activity: "Arrive in Hubli" }
        ]
      }
    ],
    includes: [
      "3 days, 2 nights accommodation",
      "All meals as per itinerary",
      "Transportation in AC vehicle",
      "Temple visits and sightseeing",
      "Boating at Honnavar backwaters",
      "Driver allowance and fuel"
    ],
    excludes: [
      "Personal expenses",
      "Entry fees to monuments",
      "Water sports activities (extra cost)",
      "GST (5%)"
    ]
  },
  {
    id: 2,
    name: "Goa Beach Paradise",
    destination: "Goa",
    days: 4,
    nights: 3,
    price: 12500,
    images: [
      "https://images.unsplash.com/photo-1561501930-6a605d0b7a9d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1523880842382-9f8d8a0c1a5a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1561501930-6a605d0b7a9d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
    ],
    description: "Explore the beaches, nightlife, and heritage of Goa",
    itinerary: [
      {
        day: 1,
        schedule: [
          { time: "8:00 AM", activity: "Pickup from Mumbai/Bangalore" },
          { time: "12:00 PM", activity: "Arrive in Goa, check-in at hotel" },
          { time: "1:00 PM", activity: "Welcome lunch" },
          { time: "3:00 PM", activity: "Visit Old Goa churches" },
          { time: "6:00 PM", activity: "Sunset at Calangute Beach" },
          { time: "8:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 2,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Dudhsagar Waterfalls trek" },
          { time: "1:00 PM", activity: "Lunch" },
          { time: "3:00 PM", activity: "Anjuna Beach and flea market" },
          { time: "6:00 PM", activity: "Water sports at Baga Beach" },
          { time: "8:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 3,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "10:00 AM", activity: "Cruise on Mandovi River" },
          { time: "1:00 PM", activity: "Lunch on cruise" },
          { time: "4:00 PM", activity: "Shopping at Panjim" },
          { time: "7:00 PM", activity: "Casino night (optional)" },
          { time: "10:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 4,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Relax at Miramar Beach" },
          { time: "12:00 PM", activity: "Check-out and back to origin" }
        ]
      }
    ],
    includes: [
      "4 days, 3 nights accommodation",
      "All meals as per itinerary",
      "Transportation in AC vehicle",
      "Sightseeing as per itinerary",
      "Cruise on Mandovi River",
      "Driver allowance and fuel"
    ],
    excludes: [
      "Personal expenses",
      "Entry fees to monuments",
      "Water sports activities (extra cost)",
      "Casino charges",
      "GST (5%)"
    ]
  },
  {
    id: 3,
    name: "Delhi Heritage Tour",
    destination: "Delhi",
    days: 3,
    nights: 2,
    price: 9500,
    images: [
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1523880842382-9f8d8a0c1a5a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1561501930-6a605d0b7a9d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
    ],
    description: "Discover the rich history and culture of India's capital",
    itinerary: [
      {
        day: 1,
        schedule: [
          { time: "8:00 AM", activity: "Pickup from airport/railway station" },
          { time: "9:00 AM", activity: "Visit Red Fort" },
          { time: "11:00 AM", activity: "Explore Chandni Chowk" },
          { time: "1:00 PM", activity: "Lunch at Paranthe Wali Gali" },
          { time: "3:00 PM", activity: "Visit Jama Masjid" },
          { time: "5:00 PM", activity: "Drive through Rajpath" },
          { time: "7:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 2,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Qutub Minar" },
          { time: "11:00 AM", activity: "Lotus Temple" },
          { time: "1:00 PM", activity: "Lunch" },
          { time: "3:00 PM", activity: "India Gate and Rashtrapati Bhavan" },
          { time: "5:00 PM", activity: "Shopping at Connaught Place" },
          { time: "8:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 3,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Humayun's Tomb" },
          { time: "11:00 AM", activity: "Akshardham Temple" },
          { time: "1:00 PM", activity: "Lunch" },
          { time: "3:00 PM", activity: "Check-out and departure" }
        ]
      }
    ],
    includes: [
      "3 days, 2 nights accommodation",
      "All meals as per itinerary",
      "Transportation in AC vehicle",
      "Sightseeing as per itinerary",
      "Driver allowance and fuel"
    ],
    excludes: [
      "Personal expenses",
      "Entry fees to monuments",
      "Camera charges",
      "GST (5%)"
    ]
  },
  {
    id: 4,
    name: "Manali Hill Station Escape",
    destination: "Manali, Himachal Pradesh",
    days: 4,
    nights: 3,
    price: 11500,
    images: [
      "https://images.unsplash.com/photo-1523880842382-9f8d8a0c1a5a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1561501930-6a605d0b7a9d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
    ],
    description: "Experience the beauty of snow-capped mountains and adventure activities",
    itinerary: [
      {
        day: 1,
        schedule: [
          { time: "7:00 AM", activity: "Pickup from Chandigarh/Delhi" },
          { time: "1:00 PM", activity: "Arrive in Manali, check-in at hotel" },
          { time: "2:00 PM", activity: "Welcome lunch" },
          { time: "4:00 PM", activity: "Visit Hadimba Temple" },
          { time: "6:00 PM", activity: "Mall Road and local market" },
          { time: "8:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 2,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Sightseeing tour of Manali" },
          { time: "1:00 PM", activity: "Lunch" },
          { time: "3:00 PM", activity: "Adventure activities (paragliding, zorbing)" },
          { time: "6:00 PM", activity: "Visit Vashist Hot Springs" },
          { time: "8:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 3,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "8:00 AM", activity: "Drive to Solang Valley" },
          { time: "10:00 AM", activity: "Adventure sports (skiing, snowboarding)" },
          { time: "1:00 PM", activity: "Lunch" },
          { time: "3:00 PM", activity: "Rope ways and sightseeing" },
          { time: "6:00 PM", activity: "Back to Manali" },
          { time: "8:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 4,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Rohtang Pass (weather permitting)" },
          { time: "1:00 PM", activity: "Lunch" },
          { time: "3:00 PM", activity: "Check-out and departure" }
        ]
      }
    ],
    includes: [
      "4 days, 3 nights accommodation",
      "All meals as per itinerary",
      "Transportation in AC vehicle",
      "Sightseeing as per itinerary",
      "Driver allowance and fuel"
    ],
    excludes: [
      "Personal expenses",
      "Entry fees to attractions",
      "Adventure sports (extra cost)",
      "Rohtang Pass permit",
      "GST (5%)"
    ]
  },
  {
    id: 5,
    name: "Kerala Backwaters & Beaches",
    destination: "Kerala",
    days: 5,
    nights: 4,
    price: 14500,
    images: [
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1523880842382-9f8d8a0c1a5a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1561501930-6a605d0b7a9d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
    ],
    description: "Experience the serene backwaters, beaches, and culture of God's Own Country",
    itinerary: [
      {
        day: 1,
        schedule: [
          { time: "8:00 AM", activity: "Pickup from Kochi Airport" },
          { time: "10:00 AM", activity: "Visit Fort Kochi and Chinese Fishing Nets" },
          { time: "12:00 PM", activity: "Lunch at local restaurant" },
          { time: "2:00 PM", activity: "Visit St. Francis Church" },
          { time: "4:00 PM", activity: "Drive to Alleppey" },
          { time: "7:00 PM", activity: "Check-in at houseboat" },
          { time: "8:00 PM", activity: "Dinner and overnight stay on houseboat" }
        ]
      },
      {
        day: 2,
        schedule: [
          { time: "6:00 AM", activity: "Morning cruise through backwaters" },
          { time: "9:00 AM", activity: "Breakfast on houseboat" },
          { time: "11:00 AM", activity: "Visit local village and coir factory" },
          { time: "1:00 PM", activity: "Lunch on houseboat" },
          { time: "3:00 PM", activity: "Continue backwater cruise" },
          { time: "6:00 PM", activity: "Disembark and drive to Kovalam" },
          { time: "9:00 PM", activity: "Dinner and overnight stay at beach resort" }
        ]
      },
      {
        day: 3,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Kovalam Beach" },
          { time: "11:00 AM", activity: "Lunch at beachside restaurant" },
          { time: "1:00 PM", activity: "Visit Napier Museum" },
          { time: "3:00 PM", activity: "Back to Kochi" },
          { time: "6:00 PM", activity: "Dinner and overnight stay at hotel" }
        ]
      },
      {
        day: 4,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Mattupetty Dam" },
          { time: "11:00 AM", activity: "Lunch at local restaurant" },
          { time: "1:00 PM", activity: "Visit Ernakulam" },
          { time: "3:00 PM", activity: "Shopping at Lulu Mall" },
          { time: "6:00 PM", activity: "Dinner and overnight stay at hotel" }
        ]
      },
      {
        day: 5,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Athirappilly Falls" },
          { time: "11:00 AM", activity: "Lunch at local restaurant" },
          { time: "1:00 PM", activity: "Visit Cherai Beach" },
          { time: "3:00 PM", activity: "Check-out and departure" }
        ]
      }
    ],
    includes: [
      "5 days, 4 nights accommodation",
      "All meals as per itinerary",
      "Transportation in AC vehicle",
      "Houseboat stay",
      "Sightseeing as per itinerary",
      "Driver allowance and fuel"
    ],
    excludes: [
      "Personal expenses",
      "Entry fees to attractions",
      "Adventure sports (extra cost)",
      "GST (5%)"
    ]
  },
  {
    id: 6,
    name: "Jaipur Royal Experience",
    destination: "Jaipur, Rajasthan",
    days: 4,
    nights: 3,
    price: 13500,
    images: [
      "https://images.unsplash.com/photo-1523880842382-9f8d8a0c1a5a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1561501930-6a605d0b7a9d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
    ],
    description: "Experience the royal heritage and majestic forts of Rajasthan",
    itinerary: [
      {
        day: 1,
        schedule: [
          { time: "8:00 AM", activity: "Pickup from Delhi" },
          { time: "12:00 PM", activity: "Arrive in Jaipur, check-in at hotel" },
          { time: "1:00 PM", activity: "Welcome lunch" },
          { time: "3:00 PM", activity: "Visit Amber Fort" },
          { time: "6:00 PM", activity: "Evening at Chokhi Dhani Village Resort" },
          { time: "9:00 PM", activity: "Dinner and cultural show" }
        ]
      },
      {
        day: 2,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit City Palace and Jantar Mantar" },
          { time: "12:00 PM", activity: "Lunch at local restaurant" },
          { time: "2:00 PM", activity: "Visit Hawa Mahal" },
          { time: "4:00 PM", activity: "Shopping at Johari Bazaar" },
          { time: "7:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 3,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Nahargarh Fort" },
          { time: "12:00 PM", activity: "Lunch at local restaurant" },
          { time: "2:00 PM", activity: "Visit Jaigarh Fort" },
          { time: "4:00 PM", activity: "Visit Albert Hall Museum" },
          { time: "7:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 4,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Galta Ji (Monkey Temple)" },
          { time: "12:00 PM", activity: "Lunch at local restaurant" },
          { time: "2:00 PM", activity: "Check-out and departure to Delhi" }
        ]
      }
    ],
    includes: [
      "4 days, 3 nights accommodation",
      "All meals as per itinerary",
      "Transportation in AC vehicle",
      "Sightseeing as per itinerary",
      "Cultural show at Chokhi Dhani",
      "Driver allowance and fuel"
    ],
    excludes: [
      "Personal expenses",
      "Entry fees to monuments",
      "Camera charges",
      "GST (5%)"
    ]
  },
  {
    id: 7,
    name: "Mumbai City Tour",
    destination: "Mumbai, Maharashtra",
    days: 3,
    nights: 2,
    price: 8500,
    images: [
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1523880842382-9f8d8a0c1a5a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1561501930-6a605d0b7a9d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
    ],
    description: "Explore the bustling metropolis of Mumbai with its iconic landmarks",
    itinerary: [
      {
        day: 1,
        schedule: [
          { time: "9:00 AM", activity: "Pickup from airport/station" },
          { time: "10:00 AM", activity: "Check-in at hotel" },
          { time: "11:00 AM", activity: "Visit Gateway of India" },
          { time: "12:00 PM", activity: "Lunch at local restaurant" },
          { time: "2:00 PM", activity: "Visit Elephanta Caves (ferry ride)" },
          { time: "6:00 PM", activity: "Back to Mumbai" },
          { time: "8:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 2,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Marine Drive" },
          { time: "10:00 AM", activity: "Visit Haji Ali Dargah" },
          { time: "12:00 PM", activity: "Lunch at local restaurant" },
          { time: "2:00 PM", activity: "Visit Chhatrapati Shivaji Terminus" },
          { time: "4:00 PM", activity: "Visit Crawford Market" },
          { time: "6:00 PM", activity: "Shopping at Colaba Causeway" },
          { time: "8:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 3,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Siddhivinayak Temple" },
          { time: "11:00 AM", activity: "Visit ISKCON Temple" },
          { time: "1:00 PM", activity: "Lunch at local restaurant" },
          { time: "3:00 PM", activity: "Check-out and departure" }
        ]
      }
    ],
    includes: [
      "3 days, 2 nights accommodation",
      "All meals as per itinerary",
      "Transportation in AC vehicle",
      "Ferry ride to Elephanta Caves",
      "Sightseeing as per itinerary",
      "Driver allowance and fuel"
    ],
    excludes: [
      "Personal expenses",
      "Entry fees to monuments",
      "Camera charges",
      "GST (5%)"
    ]
  },
  {
    id: 8,
    name: "Bangalore Tech & Gardens Tour",
    destination: "Bangalore, Karnataka",
    days: 3,
    nights: 2,
    price: 7500,
    images: [
      "https://images.unsplash.com/photo-1523880842382-9f8d8a0c1a5a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1561501930-6a605d0b7a9d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
    ],
    description: "Experience the garden city with its tech hubs and beautiful parks",
    itinerary: [
      {
        day: 1,
        schedule: [
          { time: "9:00 AM", activity: "Pickup from airport/station" },
          { time: "10:00 AM", activity: "Check-in at hotel" },
          { time: "11:00 AM", activity: "Visit Lalbagh Botanical Garden" },
          { time: "1:00 PM", activity: "Lunch at local restaurant" },
          { time: "3:00 PM", activity: "Visit Bangalore Palace" },
          { time: "5:00 PM", activity: "Visit Cubbon Park" },
          { time: "7:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 2,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit ISKCON Temple" },
          { time: "11:00 AM", activity: "Visit Nandi Hills" },
          { time: "1:00 PM", activity: "Lunch at hilltop restaurant" },
          { time: "3:00 PM", activity: "Visit Wonderla Amusement Park" },
          { time: "7:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 3,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Vidhana Soudha" },
          { time: "11:00 AM", activity: "Visit Tipu Sultan's Palace" },
          { time: "1:00 PM", activity: "Lunch at local restaurant" },
          { time: "3:00 PM", activity: "Shopping at Commercial Street" },
          { time: "5:00 PM", activity: "Check-out and departure" }
        ]
      }
    ],
    includes: [
      "3 days, 2 nights accommodation",
      "All meals as per itinerary",
      "Transportation in AC vehicle",
      "Sightseeing as per itinerary",
      "Driver allowance and fuel"
    ],
    excludes: [
      "Personal expenses",
      "Entry fees to monuments",
      "Amusement park tickets",
      "GST (5%)"
    ]
  },
  {
    id: 9,
    name: "Chennai Cultural Tour",
    destination: "Chennai, Tamil Nadu",
    days: 4,
    nights: 3,
    price: 9500,
    images: [
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1523880842382-9f8d8a0c1a5a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1561501930-6a605d0b7a9d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
    ],
    description: "Discover the cultural capital of South India with its temples and beaches",
    itinerary: [
      {
        day: 1,
        schedule: [
          { time: "9:00 AM", activity: "Pickup from airport/station" },
          { time: "10:00 AM", activity: "Check-in at hotel" },
          { time: "11:00 AM", activity: "Visit Marina Beach" },
          { time: "1:00 PM", activity: "Lunch at local restaurant" },
          { time: "3:00 PM", activity: "Visit Kapaleeshwarar Temple" },
          { time: "5:00 PM", activity: "Visit Santhome Cathedral" },
          { time: "7:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 2,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Fort St. George" },
          { time: "11:00 AM", activity: "Visit St. Mary's Church" },
          { time: "1:00 PM", activity: "Lunch at local restaurant" },
          { time: "3:00 PM", activity: "Visit Government Museum" },
          { time: "5:00 PM", activity: "Visit Valluvar Kottam" },
          { time: "7:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 3,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Mahabalipuram (UNESCO World Heritage Site)" },
          { time: "1:00 PM", activity: "Lunch at local restaurant" },
          { time: "3:00 PM", activity: "Visit Pancha Rathas" },
          { time: "5:00 PM", activity: "Visit Shore Temple" },
          { time: "7:00 PM", activity: "Back to Chennai" },
          { time: "8:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 4,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Vadapalani Murugan Temple" },
          { time: "11:00 AM", activity: "Visit Parthasarathy Temple" },
          { time: "1:00 PM", activity: "Lunch at local restaurant" },
          { time: "3:00 PM", activity: "Shopping at T. Nagar" },
          { time: "5:00 PM", activity: "Check-out and departure" }
        ]
      }
    ],
    includes: [
      "4 days, 3 nights accommodation",
      "All meals as per itinerary",
      "Transportation in AC vehicle",
      "Sightseeing as per itinerary",
      "Driver allowance and fuel"
    ],
    excludes: [
      "Personal expenses",
      "Entry fees to monuments",
      "Camera charges",
      "GST (5%)"
    ]
  },
  {
    id: 10,
    name: "Hyderabad Heritage & Cuisine",
    destination: "Hyderabad, Telangana",
    days: 3,
    nights: 2,
    price: 8500,
    images: [
      "https://images.unsplash.com/photo-1523880842382-9f8d8a0c1a5a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1561501930-6a605d0b7a9d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
    ],
    description: "Experience the rich heritage and famous cuisine of Hyderabad",
    itinerary: [
      {
        day: 1,
        schedule: [
          { time: "9:00 AM", activity: "Pickup from airport/station" },
          { time: "10:00 AM", activity: "Check-in at hotel" },
          { time: "11:00 AM", activity: "Visit Charminar" },
          { time: "1:00 PM", activity: "Lunch at local restaurant (try Hyderabadi biryani)" },
          { time: "3:00 PM", activity: "Visit Mecca Masjid" },
          { time: "5:00 PM", activity: "Visit Salar Jung Museum" },
          { time: "7:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 2,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Golconda Fort" },
          { time: "12:00 PM", activity: "Lunch at local restaurant" },
          { time: "2:00 PM", activity: "Visit Ramoji Film City" },
          { time: "6:00 PM", activity: "Shopping at Laad Bazaar" },
          { time: "8:00 PM", activity: "Dinner and overnight stay" }
        ]
      },
      {
        day: 3,
        schedule: [
          { time: "7:00 AM", activity: "Breakfast" },
          { time: "9:00 AM", activity: "Visit Birla Mandir" },
          { time: "11:00 AM", activity: "Visit Hussain Sagar Lake" },
          { time: "1:00 PM", activity: "Lunch at local restaurant" },
          { time: "3:00 PM", activity: "Visit Chowmahalla Palace" },
          { time: "5:00 PM", activity: "Check-out and departure" }
        ]
      }
    ],
    includes: [
      "3 days, 2 nights accommodation",
      "All meals as per itinerary",
      "Transportation in AC vehicle",
      "Sightseeing as per itinerary",
      "Driver allowance and fuel"
    ],
    excludes: [
      "Personal expenses",
      "Entry fees to monuments",
      "Camera charges",
      "GST (5%)"
    ]
  }
];

export default function FixedVacationPackages() {
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [showBookingForm, setShowBookingForm] = useState(false);
  const [showPackageDetails, setShowPackageDetails] = useState(false);
  const [bookingData, setBookingData] = useState({
    startDate: '',
    passengers: 1,
    vehicleType: 'economy'
  });

  const handleViewDetails = (pkg) => {
    setSelectedPackage(pkg);
    setShowPackageDetails(true);
  };

  const handleBackToPackages = () => {
    setShowPackageDetails(false);
    setSelectedPackage(null);
  };

  const handleBookNow = () => {
    setShowBookingForm(true);
  };

  const handleCancelBooking = () => {
    setShowBookingForm(false);
  };

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Create vacation booking data
      const bookingData = {
        destination: selectedPackage.destination,
        start_date: bookingData.startDate,
        end_date: new Date(new Date(bookingData.startDate).getTime() + (selectedPackage.days - 1) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        passengers: bookingData.passengers,
        vehicle_type: bookingData.vehicleType,
        total_price: selectedPackage.price,
        status: 'pending',
        hotel_name: selectedPackage.name, // Using package name as hotel name for fixed packages
        ride_included: true,
        hotel_included: true
      };
      
      // Create the vacation booking
      const response = await vacationService.createVacation(bookingData);
      
      // Schedule rides for the vacation
      if (response.id) {
        try {
          await vacationSchedulerService.scheduleVacationRides(response.id);
        } catch (scheduleError) {
          console.error('Failed to schedule vacation rides:', scheduleError);
        }
      }
      
      alert('Booking submitted successfully! A driver will review your request shortly.');
      setShowBookingForm(false);
      setSelectedPackage(null);
    } catch (error) {
      console.error('Failed to submit booking:', error);
      alert('Failed to submit booking. Please try again.');
    }
  };

  // Simple image component for package cards
  const PackageImage = ({ images, packageName }) => {
    return (
      <div className="relative">
        <img 
          src={images[0]} 
          alt={`${packageName}`} 
          className="w-full h-48 object-cover rounded-t-lg"
        />
        <div className="absolute top-4 right-4 bg-white px-3 py-1 rounded-full text-sm font-bold">
          ₹{FIXED_PACKAGES.find(p => p.name === packageName)?.price || 0}
        </div>
      </div>
    );
  };

  // Simple image gallery for package details
  const PackageImageGallery = ({ images, packageName }) => {
    return (
      <div className="mb-6">
        <img 
          src={images[0]} 
          alt={`${packageName}`} 
          className="w-full h-64 object-cover rounded-lg mb-4"
        />
      </div>
    );
  };

  if (showBookingForm && selectedPackage) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto card">
            <h2 className="text-2xl font-bold mb-6">Book {selectedPackage.name}</h2>
            
            <PackageImageGallery images={selectedPackage.images} packageName={selectedPackage.name} />
            
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">{selectedPackage.name}</h3>
              <span className="text-2xl font-bold text-primary-600">₹{selectedPackage.price}</span>
            </div>
            <p className="text-gray-600 mb-6">{selectedPackage.destination} • {selectedPackage.days}D/{selectedPackage.nights}N</p>
            
            <form onSubmit={handleBookingSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
                  <input
                    type="date"
                    value={bookingData.startDate}
                    onChange={(e) => setBookingData({...bookingData, startDate: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Passengers</label>
                  <select
                    value={bookingData.passengers}
                    onChange={(e) => setBookingData({...bookingData, passengers: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    {[1, 2, 3, 4, 5, 6].map(num => (
                      <option key={num} value={num}>{num} {num === 1 ? 'Passenger' : 'Passengers'}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Vehicle Type</label>
                  <select
                    value={bookingData.vehicleType}
                    onChange={(e) => setBookingData({...bookingData, vehicleType: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="economy">Economy</option>
                    <option value="premium">Premium</option>
                    <option value="suv">SUV</option>
                    <option value="luxury">Luxury</option>
                  </select>
                </div>
              </div>
              
              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={handleCancelBooking}
                  className="flex-1 btn-outline"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 btn-primary"
                >
                  Confirm Booking
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  if (showPackageDetails && selectedPackage) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="mb-6">
            <button
              onClick={handleBackToPackages}
              className="btn-outline"
            >
              ← Back to All Packages
            </button>
          </div>
          
          <div className="max-w-4xl mx-auto">
            <div className="card mb-8">
              <h2 className="text-2xl font-bold mb-6">{selectedPackage.name}</h2>
              
              <PackageImageGallery images={selectedPackage.images} packageName={selectedPackage.name} />
              
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold">{selectedPackage.name}</h3>
                <span className="text-2xl font-bold text-primary-600">₹{selectedPackage.price}</span>
              </div>
              <p className="text-gray-600 mb-6">{selectedPackage.destination} • {selectedPackage.days}D/{selectedPackage.nights}N</p>
              
              <p className="text-gray-700 mb-6">{selectedPackage.description}</p>
              
              <div className="flex space-x-4 mb-8">
                <button
                  onClick={handleBookNow}
                  className="flex-1 btn-primary"
                >
                  Book Now
                </button>
              </div>
            </div>
            
            <div className="card mb-8">
              <h3 className="text-xl font-bold mb-4">Package Itinerary</h3>
              
              <div className="space-y-6">
                {selectedPackage.itinerary.map((day, index) => (
                  <div key={index} className="border-l-4 border-primary-500 pl-4">
                    <h4 className="text-lg font-bold mb-3">Day {day.day}</h4>
                    <div className="space-y-3">
                      {day.schedule.map((item, itemIndex) => (
                        <div key={itemIndex} className="flex items-start">
                          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center mr-3">
                            <span className="text-primary-600 font-bold">{item.time}</span>
                          </div>
                          <div>
                            <p className="font-medium">{item.activity}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="card">
                <h4 className="text-lg font-bold mb-3">Includes</h4>
                <ul className="space-y-2">
                  {selectedPackage.includes.map((item, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="card">
                <h4 className="text-lg font-bold mb-3">Excludes</h4>
                <ul className="space-y-2">
                  {selectedPackage.excludes.map((item, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-red-500 mr-2">✗</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show all packages
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8">Fixed Vacation Packages</h1>
        <p className="text-center text-gray-600 mb-12">Choose from our curated vacation packages for a hassle-free travel experience</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {FIXED_PACKAGES.map((pkg) => (
            <div key={pkg.id} className="card hover:shadow-xl transition-shadow duration-300">
              <PackageImage images={pkg.images} packageName={pkg.name} />
              
              <div className="p-6">
                <h3 className="text-xl font-bold mb-2">{pkg.name}</h3>
                <div className="flex items-center text-gray-600 mb-3">
                  <MapPin className="w-4 h-4 mr-1" />
                  <span>{pkg.destination}</span>
                </div>
                
                <div className="flex items-center justify-between mb-4 text-sm text-gray-600">
                  <div className="flex items-center">
                    <Calendar className="w-4 h-4 mr-1" />
                    <span>{pkg.days}D/{pkg.nights}N</span>
                  </div>
                  <div className="flex items-center">
                    <Star className="w-4 h-4 mr-1 text-yellow-500" />
                    <span>4.8</span>
                  </div>
                </div>
                
                <p className="text-gray-700 mb-4">{pkg.description}</p>
                
                <button
                  onClick={() => handleViewDetails(pkg)}
                  className="w-full btn-primary"
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}