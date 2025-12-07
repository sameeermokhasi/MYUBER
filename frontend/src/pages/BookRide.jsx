import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapPin, DollarSign, Car, Clock, ArrowLeft, Search } from 'lucide-react'
import { rideService } from '../services/api'
import MapWithRoute from '../components/MapWithRoute'

export default function BookRide() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    pickup_address: '',
    pickup_lat: 0,
    pickup_lng: 0,
    destination_address: '',
    destination_lng: 0,
    vehicle_type: 'economy',
    scheduled_time: ''
  })
  const [estimatedFare, setEstimatedFare] = useState(null)
  const [loading, setLoading] = useState(false)
  const [mapRouteInfo, setMapRouteInfo] = useState(null)

  // Autocomplete states
  const [pickupSuggestions, setPickupSuggestions] = useState([])
  const [destSuggestions, setDestSuggestions] = useState([])
  const [showPickupSuggestions, setShowPickupSuggestions] = useState(false)
  const [showDestSuggestions, setShowDestSuggestions] = useState(false)

  // Comprehensive list of locations across major cities
  const popularLocations = [
    // Bangalore
    { name: 'Bangalore City Junction', lat: 12.9781, lng: 77.5697, city: 'Bangalore' },
    { name: 'Kempegowda International Airport', lat: 13.1986, lng: 77.7066, city: 'Bangalore' },
    { name: 'Indiranagar', lat: 12.9719, lng: 77.6412, city: 'Bangalore' },
    { name: 'Koramangala', lat: 12.9352, lng: 77.6245, city: 'Bangalore' },
    { name: 'Whitefield', lat: 12.9698, lng: 77.7500, city: 'Bangalore' },

    // Hubli-Dharwad
    { name: 'Hubli Junction', lat: 15.3647, lng: 75.1240, city: 'Hubli' },
    { name: 'Dharwad Railway Station', lat: 15.4589, lng: 75.0078, city: 'Dharwad' },
    { name: 'Urban Oasis Mall, Hubli', lat: 15.3524, lng: 75.1376, city: 'Hubli' },
    { name: 'PVR Cinemas, Hubli', lat: 15.3700, lng: 75.1000, city: 'Hubli' },
    { name: 'Unkal Lake, Hubli', lat: 15.3716, lng: 75.1180, city: 'Hubli' },
    { name: 'Nrupatunga Betta, Hubli', lat: 15.3800, lng: 75.1400, city: 'Hubli' },

    // Mumbai
    { name: 'Chhatrapati Shivaji Maharaj Terminus', lat: 18.9400, lng: 72.8353, city: 'Mumbai' },
    { name: 'Mumbai Airport (BOM)', lat: 19.0896, lng: 72.8656, city: 'Mumbai' },
    { name: 'Gateway of India', lat: 18.9220, lng: 72.8347, city: 'Mumbai' },
    { name: 'Marine Drive', lat: 18.9440, lng: 72.8230, city: 'Mumbai' },
    { name: 'Juhu Beach', lat: 19.0988, lng: 72.8264, city: 'Mumbai' },
    { name: 'Bandra Kurla Complex', lat: 19.0600, lng: 72.8600, city: 'Mumbai' },

    // Kolkata
    { name: 'Howrah Junction', lat: 22.5838, lng: 88.3426, city: 'Kolkata' },
    { name: 'Kolkata Airport (CCU)', lat: 22.6520, lng: 88.4463, city: 'Kolkata' },
    { name: 'Victoria Memorial', lat: 22.5448, lng: 88.3426, city: 'Kolkata' },
    { name: 'Park Street', lat: 22.5550, lng: 88.3500, city: 'Kolkata' },
    { name: 'Salt Lake City', lat: 22.5800, lng: 88.4200, city: 'Kolkata' },
    { name: 'New Market', lat: 22.5600, lng: 88.3500, city: 'Kolkata' },

    // Delhi
    { name: 'New Delhi Railway Station', lat: 28.6429, lng: 77.2191, city: 'Delhi' },
    { name: 'Indira Gandhi International Airport', lat: 28.5562, lng: 77.1000, city: 'Delhi' },
    { name: 'Connaught Place', lat: 28.6315, lng: 77.2167, city: 'Delhi' },
    { name: 'India Gate', lat: 28.6129, lng: 77.2295, city: 'Delhi' },
    { name: 'Hauz Khas Village', lat: 28.5530, lng: 77.1940, city: 'Delhi' },
    { name: 'Saket Select Citywalk', lat: 28.5280, lng: 77.2190, city: 'Delhi' }
  ]

  const handleInputChange = (field, value) => {
    console.log(`Input change: ${field}, value: ${value}`)
    if (field === 'pickup') {
      setFormData({ ...formData, pickup_address: value })
      if (value.length > 0) {
        const filtered = popularLocations.filter(loc =>
          loc.name.toLowerCase().includes(value.toLowerCase()) ||
          loc.city.toLowerCase().includes(value.toLowerCase())
        )
        console.log(`Filtered pickup suggestions: ${filtered.length}`)
        setPickupSuggestions(filtered)
        setShowPickupSuggestions(true)
      } else {
        setShowPickupSuggestions(false)
      }
    } else {
      setFormData({ ...formData, destination_address: value })
      if (value.length > 0) {
        const filtered = popularLocations.filter(loc =>
          loc.name.toLowerCase().includes(value.toLowerCase()) ||
          loc.city.toLowerCase().includes(value.toLowerCase())
        )
        setDestSuggestions(filtered)
        setShowDestSuggestions(true)
      } else {
        setShowDestSuggestions(false)
      }
    }
  }

  const handleLocationSelect = (field, location) => {
    if (field === 'pickup') {
      setFormData({
        ...formData,
        pickup_address: location.name,
        pickup_lat: location.lat,
        pickup_lng: location.lng
      })
      setShowPickupSuggestions(false)
    } else {
      setFormData({
        ...formData,
        destination_address: location.name,
        destination_lat: location.lat,
        destination_lng: location.lng
      })
      setShowDestSuggestions(false)
    }
  }

  const calculateEstimate = () => {
    if (formData.pickup_lat && formData.destination_lat) {
      // Haversine formula
      const R = 6371
      const dLat = (formData.destination_lat - formData.pickup_lat) * Math.PI / 180
      const dLon = (formData.destination_lng - formData.pickup_lng) * Math.PI / 180
      const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(formData.pickup_lat * Math.PI / 180) * Math.cos(formData.destination_lat * Math.PI / 180) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2)
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
      const distance = R * c

      const baseFare = { economy: 50, suv: 120, luxury: 200 }
      const perKmRate = { economy: 10, suv: 18, luxury: 25 }

      const fare = baseFare[formData.vehicle_type] + (distance * perKmRate[formData.vehicle_type])
      const duration = Math.round((distance / 40) * 60)

      setEstimatedFare({
        distance: distance.toFixed(1),
        duration,
        fare: fare.toFixed(2)
      })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    // Calculate estimate if not already calculated
    if (!estimatedFare) {
      calculateEstimate()
      // Wait a moment for state to update
      await new Promise(resolve => setTimeout(resolve, 100))
    }

    if (!estimatedFare || !estimatedFare.fare) {
      alert('Please select pickup and destination locations first!')
      return
    }

    setLoading(true)

    try {
      // Only send the required fields to the backend
      const rideData = {
        pickup_address: formData.pickup_address,
        pickup_lat: formData.pickup_lat,
        pickup_lng: formData.pickup_lng,
        destination_address: formData.destination_address,
        destination_lat: formData.destination_lat,
        destination_lng: formData.destination_lng,
        vehicle_type: formData.vehicle_type,
        scheduled_time: formData.scheduled_time || null
      }

      const response = await rideService.createRide(rideData)
      alert('Ride request sent successfully! Waiting for driver acceptance...')
      navigate('/rider')
    } catch (error) {
      console.error('Failed to book ride:', error)
      alert('Failed to book ride. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black">
      <div className="bg-black border-b border-dark-800 shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <button
            onClick={() => navigate('/rider')}
            className="flex items-center text-gray-400 hover:text-white"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Dashboard
          </button>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Book a Local Ride</h1>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Map View */}
            <div className="md:col-span-3 mb-6">
              <div className="card">
                <h3 className="text-lg font-bold mb-4">🗺️ Route Map</h3>
                <MapWithRoute
                  pickup={formData.pickup_lat ? {
                    lat: formData.pickup_lat,
                    lng: formData.pickup_lng,
                    address: formData.pickup_address
                  } : null}
                  destination={formData.destination_lat ? {
                    lat: formData.destination_lat,
                    lng: formData.destination_lng,
                    address: formData.destination_address
                  } : null}
                  onRouteCalculated={(info) => {
                    setMapRouteInfo(info)
                    // Auto-update fare based on actual route distance
                    const baseFare = { economy: 50, suv: 120, luxury: 200 }
                    const perKmRate = { economy: 10, suv: 18, luxury: 25 }
                    const fare = baseFare[formData.vehicle_type] + (parseFloat(info.distance) * perKmRate[formData.vehicle_type])
                    setEstimatedFare({
                      distance: info.distance,
                      duration: info.duration,
                      fare: fare.toFixed(2),
                      pickupETA: info.pickupETA,
                      dropoffETA: info.dropoffETA
                    })
                  }}
                />
              </div>
            </div>

            {/* Booking Form */}
            <div className="md:col-span-2">
              <form onSubmit={handleSubmit} className="card space-y-6">
                {/* Pickup Location */}
                <div className="relative">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <MapPin className="w-4 h-4 inline text-green-500 mr-1" />
                    Pickup Location
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value={formData.pickup_address}
                      onChange={(e) => handleInputChange('pickup', e.target.value)}
                      onFocus={() => formData.pickup_address && setShowPickupSuggestions(true)}
                      className="input-field pl-10"
                      placeholder="Search pickup location (e.g., BTM Layout)"
                      required
                      autoComplete="off"
                    />
                    <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                  </div>

                  {/* Autocomplete Dropdown */}
                  {showPickupSuggestions && pickupSuggestions.length > 0 && (
                    <div className="absolute z-50 w-full bg-dark-800 border border-dark-700 rounded-lg shadow-lg mt-1 max-h-60 overflow-y-auto">
                      {pickupSuggestions.map((loc, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onMouseDown={() => handleLocationSelect('pickup', loc)} // Use onMouseDown to prevent blur issues
                          className="w-full text-left px-4 py-2 hover:bg-dark-700 flex items-center space-x-2 transition-colors border-b border-dark-700 last:border-0"
                        >
                          <MapPin className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-200">{loc.name}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Destination */}
                <div className="relative">
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <MapPin className="w-4 h-4 inline text-red-500 mr-1" />
                    Destination
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value={formData.destination_address}
                      onChange={(e) => handleInputChange('destination', e.target.value)}
                      onFocus={() => formData.destination_address && setShowDestSuggestions(true)}
                      className="input-field pl-10"
                      placeholder="Search destination (e.g., Indiranagar)"
                      required
                      autoComplete="off"
                    />
                    <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                  </div>

                  {/* Autocomplete Dropdown */}
                  {showDestSuggestions && destSuggestions.length > 0 && (
                    <div className="absolute z-50 w-full bg-dark-800 border border-dark-700 rounded-lg shadow-lg mt-1 max-h-60 overflow-y-auto">
                      {destSuggestions.map((loc, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onMouseDown={() => handleLocationSelect('destination', loc)}
                          className="w-full text-left px-4 py-2 hover:bg-dark-700 flex items-center space-x-2 transition-colors border-b border-dark-700 last:border-0"
                        >
                          <MapPin className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-200">{loc.name}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Vehicle Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-3">Vehicle Type</label>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { value: 'economy', label: 'Economy', icon: '🚗', price: '₹50 + ₹10/km' },
                      { value: 'suv', label: 'SUV', icon: '🚐', price: '₹120 + ₹18/km' },
                      { value: 'luxury', label: 'Luxury', icon: '🚘', price: '₹200 + ₹25/km' }
                    ].map((vehicle) => (
                      <button
                        key={vehicle.value}
                        type="button"
                        onClick={() => setFormData({ ...formData, vehicle_type: vehicle.value })}
                        className={`p-4 border-2 rounded-lg text-left transition-all ${formData.vehicle_type === vehicle.value
                          ? 'border-primary-600 bg-primary-900/20'
                          : 'border-dark-600 hover:border-dark-500 bg-dark-800'
                          }`}
                      >
                        <div className="text-2xl mb-1">{vehicle.icon}</div>
                        <div className="font-semibold text-white">{vehicle.label}</div>
                        <div className="text-xs text-gray-400">{vehicle.price}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Schedule (Optional) */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <Clock className="w-4 h-4 inline mr-1" />
                    Schedule for Later (Optional)
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.scheduled_time}
                    onChange={(e) => setFormData({ ...formData, scheduled_time: e.target.value })}
                    className="input-field"
                  />
                </div>

                {/* Calculate Estimate */}


                {/* Submit */}
                <button
                  type="submit"
                  className="btn-primary w-full"
                  disabled={loading || !formData.pickup_lat || !formData.destination_lat}
                >
                  {loading ? 'Booking...' : 'Confirm Booking'}
                </button>
              </form>
            </div>

            {/* Fare Estimate */}
            <div className="md:col-span-1">
              <div className="card sticky top-6">
                <h3 className="text-lg font-bold mb-4">Fare Estimate</h3>

                {estimatedFare ? (
                  <div className="space-y-4">
                    <div className="bg-primary-900/20 rounded-lg p-4 border border-primary-900/30">
                      <p className="text-sm text-gray-400 mb-1">Estimated Fare</p>
                      <p className="text-3xl font-bold text-primary-400">
                        ₹{estimatedFare.fare}
                      </p>
                    </div>

                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Distance</span>
                        <span className="font-semibold text-white">{estimatedFare.distance} km</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Est. Duration</span>
                        <span className="font-semibold text-white">{estimatedFare.duration} min</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Vehicle</span>
                        <span className="font-semibold capitalize text-white">{formData.vehicle_type}</span>
                      </div>
                      {estimatedFare.pickupETA && (
                        <>
                          <div className="border-t pt-2 mt-2"></div>
                          <div className="flex justify-between text-green-400">
                            <span>🕒 Pickup ETA</span>
                            <span className="font-semibold">{estimatedFare.pickupETA}</span>
                          </div>
                          <div className="flex justify-between text-blue-400">
                            <span>🏁 Drop-off ETA</span>
                            <span className="font-semibold">{estimatedFare.dropoffETA}</span>
                          </div>
                        </>
                      )}
                    </div>

                    <div className="border-t border-dark-700 pt-3 mt-3">
                      <p className="text-xs text-gray-500">
                        * Actual fare may vary based on traffic and route
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Car className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                    <p className="text-gray-400 text-sm">
                      Select pickup and destination to see fare estimate
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}