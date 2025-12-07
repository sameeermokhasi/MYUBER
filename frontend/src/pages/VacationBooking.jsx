import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plane, Hotel, Car, Calendar, Users, MapPin, DollarSign, Award, LogOut, Check, Clock, Utensils, CheckCircle } from 'lucide-react'
import { vacationService } from '../services/api'
import { useAuthStore } from '../store/authStore'
import FixedVacationPackages from '../components/FixedVacationPackages';

export default function VacationBooking() {
  const [vacations, setVacations] = useState([])
  const [loyaltyPoints, setLoyaltyPoints] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showBookingForm, setShowBookingForm] = useState(false)
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  // Parse schedule data if available
  const parseSchedule = (scheduleJson) => {
    try {
      return JSON.parse(scheduleJson);
    } catch (e) {
      return null;
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [vacationsData, loyaltyData] = await Promise.all([
        vacationService.getVacations(),
        vacationService.getLoyaltyPoints()
      ])
      setVacations(vacationsData)
      setLoyaltyPoints(loyaltyData)
      setError(null)
    } catch (error) {
      console.error('Failed to load data:', error)
      setError('Failed to load vacation data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleStartNextRide = async (vacationId) => {
    try {
      if (!window.confirm('Are you sure you want to start the next ride for this vacation?')) {
        return;
      }

      const response = await vacationService.scheduleNextRide(vacationId);
      if (response) {
        alert('Next ride started successfully! Drivers have been notified.');
        // Refresh data
        loadData();
      } else {
        alert('No more rides scheduled for this vacation or next ride already active.');
      }
    } catch (error) {
      console.error('Failed to start next ride:', error);
      alert('Failed to start next ride. Please try again.');
    }
  };

  const getTierColor = (tier) => {
    const colors = {
      bronze: 'bg-orange-900/50 text-orange-200 border border-orange-700',
      silver: 'bg-gray-800 text-gray-200 border border-gray-600',
      gold: 'bg-yellow-900/50 text-yellow-200 border border-yellow-700',
      platinum: 'bg-purple-900/50 text-purple-200 border border-purple-700'
    }
    return colors[tier] || colors.bronze
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="bg-black shadow-sm border-b border-dark-800">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Plane className="w-8 h-8 text-primary-600" />
              <span className="text-2xl font-bold text-white">Automated Vacation Planner</span>
            </div>
            <div className="flex items-center space-x-4">
              <button onClick={() => navigate('/rider')} className="text-gray-300 hover:text-white">
                ← Back to Dashboard
              </button>
              <button onClick={logout} className="btn-outline text-sm">
                <LogOut className="w-4 h-4 inline mr-1" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 rounded-2xl p-8 text-white mb-8">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h1 className="text-4xl font-bold mb-4">Your Automated Vacation Planner</h1>
              <p className="text-lg text-purple-100 mb-6">
                Create a complete travel schedule with transportation, accommodation, and activities.
                Our system will automatically arrange all your rides based on your schedule.
              </p>
              <button
                onClick={() => navigate('/rider/vacation-planner')}
                className="bg-white text-purple-600 hover:bg-gray-100 font-semibold py-3 px-8 rounded-lg transition-colors duration-200 mr-4"
              >
                Create Custom Plan
              </button>
              <button
                onClick={() => navigate('/rider/fixed-packages')}
                className="bg-transparent border-2 border-white text-white hover:bg-white hover:text-purple-600 font-semibold py-3 px-8 rounded-lg transition-colors duration-200"
              >
                View Fixed Packages
              </button>
            </div>

            {/* Loyalty Card */}
            {loyaltyPoints && (
              <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-xl p-6 ml-8">
                <div className="flex items-center space-x-2 mb-2">
                  <Award className="w-6 h-6" />
                  <h3 className="text-xl font-bold">Loyalty Status</h3>
                </div>
                <p className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getTierColor(loyaltyPoints.tier)} mb-2`}>
                  {loyaltyPoints.tier.toUpperCase()} TIER
                </p>
                <p className="text-2xl font-bold">{loyaltyPoints.total_points} Points</p>
                <p className="text-sm text-purple-100 mt-2">{loyaltyPoints.benefits}</p>
              </div>
            )}
          </div>
        </div>

        {/* How It Works */}
        <div className="card mb-8 bg-dark-800 border border-dark-700">
          <h2 className="text-2xl font-bold mb-6 text-white">How Our Automated Vacation Planner Works</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-dark-900 rounded-lg border border-dark-700">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">1</div>
              <h3 className="text-lg font-bold mb-2 text-white">Create Your Schedule</h3>
              <p className="text-gray-400">Enter your flight details, meal preferences, and activities for each day</p>
            </div>
            <div className="text-center p-6 bg-dark-900 rounded-lg border border-dark-700">
              <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">2</div>
              <h3 className="text-lg font-bold mb-2 text-white">Automatic Ride Booking</h3>
              <p className="text-gray-400">Our system automatically books rides 30 minutes before each activity</p>
            </div>
            <div className="text-center p-6 bg-dark-900 rounded-lg border border-dark-700">
              <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">3</div>
              <h3 className="text-lg font-bold mb-2 text-white">Enjoy Your Trip</h3>
              <p className="text-gray-400">Sit back and relax while we handle all your transportation needs</p>
            </div>
          </div>
        </div>

        {/* My Vacations */}
        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">My Vacation Bookings</h2>
            <button
              onClick={loadData}
              className="text-primary-600 hover:text-primary-500 text-sm font-semibold flex items-center"
            >
              <Clock className="w-4 h-4 mr-1" />
              Refresh
            </button>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500 text-red-500 p-4 rounded-lg mb-6">
              {error}
            </div>
          )}

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            </div>
          ) : vacations.length === 0 ? (
            <div className="text-center py-12">
              <Plane className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No vacation bookings yet</p>
              <p className="text-gray-400 mt-2">Start planning your dream vacation!</p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 gap-6">
              {vacations.map((vacation) => {
                const schedule = vacation.schedule ? parseSchedule(vacation.schedule) : null;
                // Mock completion status for demo purposes
                // In a real app, this would come from the backend based on completed rides
                const isCompleted = vacation.status === 'completed';
                const currentLeg = vacation.completed_rides_count || 0;

                return (
                  <div key={vacation.id} className="border border-gray-200 rounded-xl p-6 hover:border-primary-300 transition-colors relative overflow-hidden">
                    {/* Vacation Completed Banner */}
                    {isCompleted && (
                      <div className="absolute top-0 left-0 right-0 bg-green-500 text-white text-center py-1 font-bold text-sm z-10">
                        VACATION COMPLETED
                      </div>
                    )}

                    <div className="flex justify-between items-start mb-4 mt-2">
                      <div>
                        <div className="flex items-center space-x-2 mb-2">
                          <MapPin className="w-5 h-5 text-primary-600" />
                          <h3 className="text-xl font-bold">{vacation.destination}</h3>
                        </div>
                        <p className="text-sm text-gray-600">Booking #{vacation.booking_reference}</p>
                      </div>
                      <span className={`badge ${vacation.status === 'confirmed' ? 'badge-success' :
                        vacation.status === 'pending' ? 'badge-warning' :
                          vacation.status === 'cancelled' ? 'badge-danger' :
                            vacation.status === 'completed' ? 'bg-green-100 text-green-800' : 'badge'
                        }`}>
                        {vacation.status.toUpperCase()}
                      </span>
                    </div>

                    <div className="space-y-3 mb-4">
                      <div className="flex items-center text-sm text-gray-600">
                        <Calendar className="w-4 h-4 mr-2" />
                        {new Date(vacation.start_date).toLocaleDateString()} - {new Date(vacation.end_date).toLocaleDateString()}
                      </div>

                      {/* Interactive Checklist - Only for Custom Plans */}
                      {schedule && !vacation.is_fixed_package && (
                        <div className="mt-4 border border-dark-700 rounded-lg overflow-hidden">
                          <div className="bg-dark-900 px-4 py-2 border-b border-dark-700 font-semibold text-sm flex items-center text-white">
                            <CheckCircle className="w-4 h-4 mr-2 text-primary-500" />
                            Trip Checklist
                          </div>
                          <div className="divide-y divide-dark-700">
                            {/* Home to Airport */}
                            <div className="px-4 py-2 flex items-center text-sm">
                              <div className={`w-5 h-5 rounded-full border flex items-center justify-center mr-3 ${isCompleted || currentLeg > 0 ? 'bg-green-600 border-green-600 text-white' : 'border-gray-500'
                                }`}>
                                {(isCompleted || currentLeg > 0) && <Check className="w-3 h-3" />}
                              </div>
                              <span className={isCompleted || currentLeg > 0 ? 'text-gray-400 line-through' : 'text-gray-300'}>
                                Home to Airport
                              </span>
                            </div>

                            {/* Flight/Train */}
                            {schedule.flightDetails && (
                              <div className="px-4 py-2 flex items-center text-sm">
                                <div className={`w-5 h-5 rounded-full border flex items-center justify-center mr-3 ${isCompleted || currentLeg > 1 ? 'bg-green-600 border-green-600 text-white' : 'border-gray-500'
                                  }`}>
                                  {(isCompleted || currentLeg > 1) && <Check className="w-3 h-3" />}
                                </div>
                                <span className={isCompleted || currentLeg > 1 ? 'text-gray-400 line-through' : 'text-gray-300'}>
                                  Travel to Destination
                                </span>
                              </div>
                            )}

                            {/* Activities */}
                            {vacation.activities && (() => {
                              try {
                                const activitiesList = JSON.parse(vacation.activities);
                                return activitiesList.map((activity, idx) => (
                                  <div key={`activity-${idx}`} className="px-4 py-2 flex items-center text-sm">
                                    <div className={`w-5 h-5 rounded-full border flex items-center justify-center mr-3 ${isCompleted || currentLeg > 2 ? 'bg-green-600 border-green-600 text-white' : 'border-gray-500'
                                      }`}>
                                      {(isCompleted || currentLeg > 2) && <Check className="w-3 h-3" />}
                                    </div>
                                    <span className={isCompleted || currentLeg > 2 ? 'text-gray-400 line-through' : 'text-gray-300'}>
                                      {activity.location}: {activity.description}
                                    </span>
                                  </div>
                                ));
                              } catch (e) {
                                // Fallback if parsing fails or old format
                                return (
                                  <div className="px-4 py-2 flex items-center text-sm">
                                    <div className={`w-5 h-5 rounded-full border flex items-center justify-center mr-3 ${isCompleted || currentLeg > 2 ? 'bg-green-600 border-green-600 text-white' : 'border-gray-500'
                                      }`}>
                                      {(isCompleted || currentLeg > 2) && <Check className="w-3 h-3" />}
                                    </div>
                                    <span className={isCompleted || currentLeg > 2 ? 'text-gray-400 line-through' : 'text-gray-300'}>
                                      Vacation Activities
                                    </span>
                                  </div>
                                );
                              }
                            })()}

                            {/* Airport to Home */}
                            <div className="px-4 py-2 flex items-center text-sm">
                              <div className={`w-5 h-5 rounded-full border flex items-center justify-center mr-3 ${isCompleted ? 'bg-green-600 border-green-600 text-white' : 'border-gray-500'
                                }`}>
                                {isCompleted && <Check className="w-3 h-3" />}
                              </div>
                              <span className={isCompleted ? 'text-gray-400 line-through' : 'text-gray-300'}>
                                Airport to Home
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="flex justify-between items-center mt-4">
                      <div className="flex items-center">
                        <span className="text-xl font-bold text-green-600 mr-1">₹</span>
                        <span className="text-xl font-bold">{vacation.total_price?.toFixed(2)}</span>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex space-x-2">
                        {vacation.status === 'confirmed' && !isCompleted && !vacation.is_fixed_package && !vacation.has_active_ride && (
                          <button
                            onClick={() => handleStartNextRide(vacation.id)}
                            className="btn-primary flex items-center px-4 py-2 text-sm"
                          >
                            <Car className="w-4 h-4 mr-2" />
                            Start Next Leg
                          </button>
                        )}
                        {vacation.has_active_ride && !isCompleted && (
                          <button className="bg-yellow-100 text-yellow-800 px-4 py-2 rounded-lg text-sm font-medium cursor-default flex items-center">
                            <Clock className="w-4 h-4 mr-2" />
                            Ride in Progress
                          </button>
                        )}
                        {isCompleted && (
                          <button className="bg-gray-100 text-gray-600 px-4 py-2 rounded-lg text-sm font-medium cursor-default flex items-center">
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Completed
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}