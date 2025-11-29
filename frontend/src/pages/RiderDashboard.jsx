import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Car, MapPin, Clock, DollarSign, LogOut, Plane, AlertCircle, CheckCircle, Navigation as NavIcon, XCircle, Menu, User, Wallet, History, X } from 'lucide-react'
import { rideService, userService } from '../services/api'
import { useAuthStore } from '../store/authStore'
import { websocketService } from '../services/websocket'
import DriverRouteMap from '../components/DriverRouteMap'
import VacationSchedulePlanner from '../components/VacationSchedulePlanner'

// Add CSS animations
const styles = `
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  @keyframes slideIn {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
  }
  
  @keyframes pulseSlow {
    0% { transform: scale(1); }
    50% { transform: scale(1.02); }
    100% { transform: scale(1); }
  }
  
  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
  }
  
  .animate-fade-in {
    animation: fadeIn 0.3s ease-out;
  }
  
  .animate-slide-in {
    animation: slideIn 0.3s ease-out;
  }
  
  .animate-pulse-slow {
    animation: pulseSlow 3s infinite;
  }
  
  .animate-bounce {
    animation: bounce 2s infinite;
  }
`;

// Inject styles
const styleSheet = document.createElement("style");
styleSheet.innerText = styles;
document.head.appendChild(styleSheet);

export default function RiderDashboard() {
  // Add static background images
  useEffect(() => {
    // Create background container
    const backgroundContainer = document.createElement('div');
    backgroundContainer.id = 'rider-dashboard-background';
    backgroundContainer.className = 'fixed inset-0 pointer-events-none z-0 overflow-hidden';
    backgroundContainer.style.zIndex = '-1'; // Ensure it's behind the main content
    
    // Add a subtle dark translucent overlay for better contrast
    const overlay = document.createElement('div');
    overlay.className = 'absolute inset-0 bg-gray-900';
    overlay.style.opacity = '0.1';
    backgroundContainer.appendChild(overlay);
    
    // Add a large background image that covers the entire background
    const backgroundImage = document.createElement('div');
    backgroundImage.className = 'absolute inset-0 bg-cover bg-center opacity-20';
    backgroundImage.style.backgroundImage = 'url(https://images.unsplash.com/photo-1502836059532-1c3cbfc953f0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80)';
    backgroundImage.style.backgroundSize = 'cover';
    backgroundImage.style.backgroundPosition = 'center';
    backgroundImage.style.zIndex = '-1';
    backgroundContainer.appendChild(backgroundImage);
    
    // Add subtle overlay elements
    const streetLightsOverlay = document.createElement('div');
    streetLightsOverlay.className = 'absolute top-0 left-0 right-0 h-20';
    streetLightsOverlay.style.backgroundImage = 'url(https://images.unsplash.com/photo-1502836059532-1c3cbfc953f0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80)';
    streetLightsOverlay.style.opacity = '0.15';
    backgroundContainer.appendChild(streetLightsOverlay);
    
    document.body.appendChild(backgroundContainer);
    
    // Cleanup function
    return () => {
      if (document.getElementById('rider-dashboard-background')) {
        document.getElementById('rider-dashboard-background').remove();
      }
    };
  }, []);
  const [rides, setRides] = useState([])
  const [loading, setLoading] = useState(true)
  const [driverLocations, setDriverLocations] = useState({})
  const [showVacationPlanner, setShowVacationPlanner] = useState(false)
  const [showMenu, setShowMenu] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  const [showWallet, setShowWallet] = useState(false)
  const [showRidesHistory, setShowRidesHistory] = useState(false)
  const [showCancelledRides, setShowCancelledRides] = useState(false)
  const [walletBalance, setWalletBalance] = useState(0)
  const [consecutiveCancellations, setConsecutiveCancellations] = useState(0)
  const [profileData, setProfileData] = useState({
    name: '',
    email: '',
    phone: '',
    address: ''
  })
  const { user, logout, updateUser } = useAuthStore()

  useEffect(() => {
    loadRides()
    // Load user profile data
    if (user) {
      setProfileData({
        name: user.name || '',
        email: user.email || '',
        phone: user.phone || '',
        address: user.address || ''
      })
      // Initialize wallet balance (in a real app, this would come from the backend)
      setWalletBalance(user.wallet_balance || 0)
      // Initialize consecutive cancellations count
      setConsecutiveCancellations(user.consecutive_cancellations || 0)
    }
    // Auto-refresh every 5 seconds for real-time updates
    const interval = setInterval(loadRides, 5000)
    return () => clearInterval(interval)
  }, [user])

  // WebSocket listener for real-time updates
  useEffect(() => {
    const handleWebSocketMessage = (data) => {
      if (data.type === 'driver_location_update') {
        // Update driver location for a specific ride
        setDriverLocations(prev => ({
          ...prev,
          [data.ride_id]: {
            lat: data.lat,
            lng: data.lng
          }
        }))
      } else if (data.type === 'ride_status_update') {
        // Refresh rides when status changes
        loadRides()
        // Show notification based on status
        const rideId = data.ride_id;
        const status = data.status;
        
        // Show browser notification
        if (Notification.permission === 'granted') {
          let title = '';
          let body = '';
          
          switch(status) {
            case 'accepted':
              title = 'Ride Accepted!';
              body = 'A driver has accepted your ride request. Your driver is on the way!';
              break;
            case 'in_progress':
              title = 'Ride Started!';
              body = 'Your ride is now in progress. Enjoy your journey!';
              break;
            case 'completed':
              title = 'Ride Completed!';
              body = 'Your ride has been completed. Thank you for using our service!';
              break;
            case 'cancelled':
              title = 'Ride Cancelled';
              body = 'Your ride has been cancelled. We apologize for the inconvenience.';
              break;
            default:
              return;
          }
          
          new Notification(title, {
            body: body,
            icon: '/favicon.ico'
          });
        }
        
        // Show alert for critical status changes
        switch(status) {
          case 'accepted':
            // Don't show alert for accepted as it might be disruptive
            break;
          case 'in_progress':
            // Don't show alert for in_progress as it might be disruptive
            break;
          case 'completed':
            // Reset consecutive cancellations when a ride is completed
            setConsecutiveCancellations(0);
            alert('Your ride has been completed! Thank you for using our service.');
            break;
          case 'cancelled':
            alert('Your ride has been cancelled by the driver. We apologize for the inconvenience.');
            break;
          default:
            break;
        }
      } else if (data.type === 'vacation_status_update') {
        // Refresh vacations when status changes
        loadRides()
      }
    }

    websocketService.addListener('message', handleWebSocketMessage)
    
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
    
    return () => {
      websocketService.removeListener('message', handleWebSocketMessage)
    }
  }, [])

  const loadRides = async () => {
    try {
      const data = await rideService.getRides()
      setRides(data)
    } catch (error) {
      console.error('Failed to load rides:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'badge-warning',
      accepted: 'badge-info',
      in_progress: 'badge-info',
      completed: 'badge-success',
      cancelled: 'badge-danger'
    }
    return badges[status] || 'badge'
  }

  const getStatusIcon = (status) => {
    switch(status) {
      case 'pending':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />
      case 'accepted':
        return <CheckCircle className="w-5 h-5 text-blue-600" />
      case 'in_progress':
        return <NavIcon className="w-5 h-5 text-purple-600" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      default:
        return <AlertCircle className="w-5 h-5 text-gray-600" />
    }
  }

  const getStatusText = (status) => {
    switch(status) {
      case 'pending':
        return '⏳ Finding driver...'
      case 'accepted':
        return '✅ Driver accepted! Arriving soon...'
      case 'in_progress':
        return '🚗 Ride in progress'
      case 'completed':
        return '✅ Ride completed'
      case 'cancelled':
        return '❌ Ride cancelled'
      default:
        return status
    }
  }

  // Get active ride (accepted or in progress)
  const activeRide = rides.find(ride => 
    ride.status === 'accepted' || ride.status === 'in_progress'
  )

  // Add useEffect to trigger notifications when ride status changes
  useEffect(() => {
    // This will be handled by WebSocket updates already
  }, [rides])

  const handleCancelRide = async (rideId) => {
    if (window.confirm('Are you sure you want to cancel this ride?')) {
      try {
        await rideService.cancelRide(rideId);
        
        // Update consecutive cancellations count
        const newCount = consecutiveCancellations + 1;
        setConsecutiveCancellations(newCount);
        
        // If more than 2 consecutive cancellations, apply penalty
        if (newCount > 2) {
          alert('You have cancelled more than 2 rides consecutively. A penalty of ₹100 will be applied to your next ride.');
        }
        
        alert('Ride cancelled successfully');
        loadRides();
      } catch (error) {
        console.error('Failed to cancel ride:', error);
        alert('Failed to cancel ride. Please try again.');
      }
    }
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    try {
      // Call API to update user profile
      const updatedUser = await userService.updateUserProfile(profileData);
      // Update the local state and auth store
      updateUser({ ...user, ...profileData });
      alert('Profile updated successfully!');
      setShowProfile(false);
    } catch (error) {
      console.error('Failed to update profile:', error);
      alert('Failed to update profile. Please try again.');
    }
  };

  const handleAddMoney = (amount) => {
    setWalletBalance(walletBalance + amount);
    alert(`₹${amount} added to your wallet successfully!`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm relative">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Car className="w-8 h-8 text-primary-600" />
              <span className="text-2xl font-bold text-gray-900">Uber Vacation</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700 animate-fade-in">Welcome, {user?.name}</span>
              <button 
                onClick={() => setShowMenu(!showMenu)}
                className="p-2 rounded-lg hover:bg-gray-100 transition-all duration-300 transform hover:scale-110"
              >
                <Menu className="w-6 h-6 text-gray-700 animate-pulse" />
              </button>
            </div>
          </div>
        </div>
        
        {/* Dropdown Menu */}
        {showMenu && (
          <div className="absolute right-6 top-16 w-64 bg-white rounded-lg shadow-xl z-50 border border-gray-200">
            <div className="py-2">
              <button 
                onClick={() => {
                  setShowMenu(false);
                  setShowProfile(true);
                }}
                className="w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center transition-colors duration-300"
              >
                <User className="w-5 h-5 mr-3 text-gray-600 animate-pulse" />
                <span>Profile</span>
              </button>
              <button 
                onClick={() => {
                  setShowMenu(false);
                  setShowWallet(true);
                }}
                className="w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center transition-colors duration-300"
              >
                <Wallet className="w-5 h-5 mr-3 text-gray-600" />
                <span>Wallet</span>
                <span className="ml-auto text-sm font-medium text-green-600 animate-pulse-slow">₹{walletBalance.toFixed(2)}</span>
              </button>
              <button 
                onClick={() => {
                  setShowMenu(false);
                  setShowRidesHistory(true);
                }}
                className="w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center transition-colors duration-300"
              >
                <History className="w-5 h-5 mr-3 text-gray-600 animate-slide-in" />
                <span>Rides History</span>
              </button>
              <button 
                onClick={() => {
                  setShowMenu(false);
                  setShowCancelledRides(true);
                }}
                className="w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center transition-colors duration-300"
              >
                <XCircle className="w-5 h-5 mr-3 text-gray-600 animate-slide-in" />
                <span>Cancelled Rides</span>
              </button>
              <div className="border-t border-gray-200 my-1"></div>
              <button 
                onClick={logout}
                className="w-full text-left px-4 py-3 hover:bg-red-50 flex items-center text-red-600 transition-colors duration-300"
              >
                <LogOut className="w-5 h-5 mr-3 animate-bounce" />
                <span>Logout</span>
              </button>
              <button 
                onClick={async () => {
                  try {
                    // In a real app, this would call an API to reset cancellations
                    // For now, we'll just reset the local state
                    setConsecutiveCancellations(0);
                    // Update user object in auth store
                    if (user) {
                      updateUser({ ...user, consecutive_cancellations: 0 });
                    }
                    setShowMenu(false);
                    alert('Consecutive cancellations reset successfully!');
                  } catch (error) {
                    console.error('Failed to reset cancellations:', error);
                    alert('Failed to reset cancellations. Please try again.');
                  }
                }}
                className="w-full text-left px-4 py-3 hover:bg-blue-50 flex items-center text-blue-600 transition-colors duration-300"
              >
                <span className="animate-pulse-slow">Reset Cancellations</span>
              </button>
            </div>
          </div>
        )}
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Vacation Planner Toggle */}
        <div className="mb-6">
          <button
            onClick={() => setShowVacationPlanner(!showVacationPlanner)}
            className="btn-primary"
          >
            {showVacationPlanner ? 'Hide Vacation Planner' : 'Show Vacation Planner'}
          </button>
        </div>
        
        {/* Vacation Schedule Planner */}
        {showVacationPlanner && (
          <div className="mb-8">
            <VacationSchedulePlanner />
          </div>
        )}
        
        {/* Quick Actions */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Link to="/rider/book" className="card hover:shadow-xl transition-all duration-300 text-center">
            <Car className="w-12 h-12 text-primary-600 mx-auto mb-3" />
            <h3 className="text-xl font-bold mb-2">Book Local Ride</h3>
            <p className="text-gray-600">Quick rides within your city</p>
          </Link>

          <Link to="/vacation" className="card hover:shadow-xl transition-all duration-300 text-center">
            <Plane className="w-12 h-12 text-primary-600 mx-auto mb-3" />
            <h3 className="text-xl font-bold mb-2">Plan Vacation</h3>
            <p className="text-gray-600">Complete travel packages</p>
          </Link>
          
        </div>

        {/* Active Ride with Real-time Map */}
        {activeRide && (
          <div className="card mb-8">
            <h2 className="text-2xl font-bold mb-4">📍 Active Ride</h2>
            <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(activeRide.status)}
                  <div>
                    <p className="font-bold text-lg">{getStatusText(activeRide.status)}</p>
                    <p className="text-xs text-gray-500">Ride #{activeRide.id}</p>
                  </div>
                </div>
                <span className={`${getStatusBadge(activeRide.status)} text-xs`}>
                  {activeRide.status.toUpperCase()}
                </span>
              </div>
            </div>
            
            {/* Detailed Progress Bar */}
            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Requested</span>
                <span>Accepted</span>
                <span>In Progress</span>
                <span>Completed</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div className={`h-3 rounded-full transition-all duration-1000 ${
                  activeRide.status === 'pending' ? 'bg-yellow-500 w-1/4' :
                  activeRide.status === 'accepted' ? 'bg-blue-500 w-1/2' :
                  activeRide.status === 'in_progress' ? 'bg-purple-500 w-3/4' :
                  'bg-green-500 w-full'
                }`}></div>
              </div>
            </div>
            
            {/* Real-time Map */}
            <DriverRouteMap 
              ride={activeRide} 
              driverLocation={driverLocations[activeRide.id]} 
            />
          </div>
        )}

        {/* Recent Rides */}
        <div className="card mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">My Rides</h2>
            <span className="text-sm text-gray-500">Auto-updating every 5s</span>
          </div>
          
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading rides...</p>
            </div>
          ) : rides.length === 0 ? (
            <div className="text-center py-12">
              <Car className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No rides yet</p>
              <p className="text-gray-400 mt-2">Book your first ride to get started!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {rides.filter(ride => ride.status !== 'completed').slice(0, 5).map((ride) => (
                <div key={ride.id} className={`border-2 rounded-lg p-5 transition-all ${
                  ride.status === 'pending' ? 'border-yellow-300 bg-yellow-50' :
                  ride.status === 'accepted' ? 'border-blue-300 bg-blue-50' :
                  ride.status === 'in_progress' ? 'border-purple-300 bg-purple-50' :
                  ride.status === 'completed' ? 'border-green-200 bg-green-50' :
                  'border-gray-200'
                }`}>
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(ride.status)}
                      <div>
                        <p className="font-bold text-lg">{getStatusText(ride.status)}</p>
                        <p className="text-xs text-gray-500">Ride #{ride.id}</p>
                      </div>
                    </div>
                    <span className={`${getStatusBadge(ride.status)} text-xs`}>
                      {ride.status.toUpperCase()}
                    </span>
                  </div>
                  
                  {/* Progress Bar for All Rides */}
                  <div className="mb-4">
                    <div className="flex justify-between text-xs text-gray-600 mb-2">
                      <span>Requested</span>
                      <span>Accepted</span>
                      <span>In Progress</span>
                      <span>Completed</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div className={`h-3 rounded-full transition-all duration-1000 ${
                        ride.status === 'pending' ? 'bg-yellow-500 w-1/4' :
                        ride.status === 'accepted' ? 'bg-blue-500 w-1/2' :
                        ride.status === 'in_progress' ? 'bg-purple-500 w-3/4' :
                        'bg-green-500 w-full'
                      }`}></div>
                    </div>
                  </div>
                  
                  <div className="flex-1 mb-3">
                    <div className="flex items-center space-x-2 mb-2">
                      <MapPin className="w-4 h-4 text-green-600" />
                      <span className="font-medium">{ride.pickup_address}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <MapPin className="w-4 h-4 text-red-600" />
                      <span className="font-medium">{ride.destination_address}</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center text-sm text-gray-600 pt-3 border-t">
                    <div className="flex items-center space-x-4">
                      <span className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        {new Date(ride.created_at).toLocaleDateString()}
                      </span>
                      {ride.distance_km && (
                        <span>{ride.distance_km.toFixed(1)} km</span>
                      )}
                    </div>
                    {ride.estimated_fare && (
                      <span className="flex items-center font-semibold text-primary-600 text-lg">
                        ₹{ride.estimated_fare.toFixed(2)}
                      </span>
                    )}
                  </div>
                  {/* Cancel button for pending rides */}
                  {ride.status === 'pending' && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <button
                        onClick={() => handleCancelRide(ride.id)}
                        className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 rounded-lg transition-colors flex items-center justify-center"
                      >
                        <XCircle className="w-4 h-4 mr-2" />
                        Cancel Ride
                      </button>
                    </div>
                  )}
                  {/* Special message for accepted rides */}
                  {ride.status === 'accepted' && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-sm text-blue-600 font-medium">
                        🚗 Your driver is on the way! Please wait at the pickup location.
                      </p>
                    </div>
                  )}
                  {/* Special message for in_progress rides */}
                  {ride.status === 'in_progress' && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-sm text-purple-600 font-medium">
                        🚙 Your ride is in progress. Enjoy your journey!
                      </p>
                    </div>
                  )}
                </div>
              ))}

            </div>
          )}
        </div>


      </div>
      
      {/* Rides History Modal */}
      {showRidesHistory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto animate-fade-in">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">📚 Rides History</h2>
                <button 
                  onClick={() => setShowRidesHistory(false)}
                  className="p-2 hover:bg-gray-100 rounded-full"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200 animate-pulse-slow">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Completed Rides</span>
                  {consecutiveCancellations > 0 && (
                    <span className="text-sm font-medium text-red-600">
                      {consecutiveCancellations} consecutive cancellations
                    </span>
                  )}
                </div>
                {consecutiveCancellations > 2 && (
                  <div className="mt-2 text-red-700 font-medium">
                    ⚠️ Penalty of ₹100 will be applied to your next ride
                  </div>
                )}
              </div>
              
              {loading ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
                  <p className="mt-4 text-gray-600">Loading ride history...</p>
                </div>
              ) : rides.filter(ride => ride.status === 'completed').length === 0 ? (
                <div className="text-center py-12">
                  <Car className="w-16 h-16 text-gray-300 mx-auto mb-4 animate-bounce" />
                  <p className="text-gray-500 text-lg">No completed rides yet</p>
                  <p className="text-gray-400 mt-2">Your completed rides will appear here</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {rides.filter(ride => ride.status === 'completed').map((ride) => (
                    <div key={ride.id} className="border-2 border-green-200 bg-green-50 rounded-lg p-5 hover:shadow-md transition-all duration-300 animate-slide-in">
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(ride.status)}
                          <div>
                            <p className="font-bold text-lg">{getStatusText(ride.status)}</p>
                            <p className="text-xs text-gray-500">Ride #{ride.id}</p>
                          </div>
                        </div>
                        <span className={`${getStatusBadge(ride.status)} text-xs`}>
                          {ride.status.toUpperCase()}
                        </span>
                      </div>
                      
                      <div className="flex-1 mb-3">
                        <div className="flex items-center space-x-2 mb-2">
                          <MapPin className="w-4 h-4 text-green-600" />
                          <span className="font-medium">{ride.pickup_address}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <MapPin className="w-4 h-4 text-red-600" />
                          <span className="font-medium">{ride.destination_address}</span>
                        </div>
                      </div>
                      <div className="flex justify-between items-center text-sm text-gray-600 pt-3 border-t">
                        <div className="flex items-center space-x-4">
                          <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            {new Date(ride.created_at).toLocaleDateString()}
                          </span>
                          {ride.distance_km && (
                            <span>{ride.distance_km.toFixed(1)} km</span>
                          )}
                        </div>
                        {ride.estimated_fare && (
                          <span className="flex items-center font-semibold text-primary-600 text-lg">
                            ₹{ride.estimated_fare.toFixed(2)}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Cancelled Rides Modal */}
      {showCancelledRides && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto animate-fade-in">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">❌ Cancelled Rides</h2>
                <button 
                  onClick={() => setShowCancelledRides(false)}
                  className="p-2 hover:bg-gray-100 rounded-full"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="mb-4 p-4 bg-red-50 rounded-lg border border-red-200">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Cancelled Rides</span>
                  {consecutiveCancellations > 0 && (
                    <span className="text-sm font-medium text-red-600">
                      {consecutiveCancellations} consecutive cancellations
                    </span>
                  )}
                </div>
                {consecutiveCancellations > 2 && (
                  <div className="mt-2 text-red-700 font-medium">
                    ⚠️ Penalty of ₹100 will be applied to your next ride
                  </div>
                )}
              </div>
              
              {loading ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
                  <p className="mt-4 text-gray-600">Loading cancelled rides...</p>
                </div>
              ) : rides.filter(ride => ride.status === 'cancelled').length === 0 ? (
                <div className="text-center py-12">
                  <XCircle className="w-16 h-16 text-gray-300 mx-auto mb-4 animate-bounce" />
                  <p className="text-gray-500 text-lg">No cancelled rides yet</p>
                  <p className="text-gray-400 mt-2">Your cancelled rides will appear here</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {rides.filter(ride => ride.status === 'cancelled').map((ride) => (
                    <div key={ride.id} className="border-2 border-red-200 bg-red-50 rounded-lg p-5 hover:shadow-md transition-all duration-300 animate-slide-in">
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(ride.status)}
                          <div>
                            <p className="font-bold text-lg">{getStatusText(ride.status)}</p>
                            <p className="text-xs text-gray-500">Ride #{ride.id}</p>
                          </div>
                        </div>
                        <span className={`${getStatusBadge(ride.status)} text-xs`}>
                          {ride.status.toUpperCase()}
                        </span>
                      </div>
                      
                      <div className="flex-1 mb-3">
                        <div className="flex items-center space-x-2 mb-2">
                          <MapPin className="w-4 h-4 text-green-600" />
                          <span className="font-medium">{ride.pickup_address}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <MapPin className="w-4 h-4 text-red-600" />
                          <span className="font-medium">{ride.destination_address}</span>
                        </div>
                      </div>
                      <div className="flex justify-between items-center text-sm text-gray-600 pt-3 border-t">
                        <div className="flex items-center space-x-4">
                          <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            {new Date(ride.created_at).toLocaleDateString()}
                          </span>
                          {ride.distance_km && (
                            <span>{ride.distance_km.toFixed(1)} km</span>
                          )}
                        </div>
                        {ride.estimated_fare && (
                          <span className="flex items-center font-semibold text-primary-600 text-lg">
                            ₹{ride.estimated_fare.toFixed(2)}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Profile Modal */}
      {showProfile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Profile</h2>
                <button 
                  onClick={() => setShowProfile(false)}
                  className="p-2 hover:bg-gray-100 rounded-full"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <form onSubmit={handleProfileUpdate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                  <input
                    type="text"
                    value={profileData.name}
                    onChange={(e) => setProfileData({...profileData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={profileData.email}
                    onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input
                    type="tel"
                    value={profileData.phone}
                    onChange={(e) => setProfileData({...profileData, phone: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                  <textarea
                    value={profileData.address}
                    onChange={(e) => setProfileData({...profileData, address: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div className="flex space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowProfile(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                  >
                    Save Changes
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
      
      {/* Wallet Modal */}
      {showWallet && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Wallet</h2>
                <button 
                  onClick={() => setShowWallet(false)}
                  className="p-2 hover:bg-gray-100 rounded-full"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="text-center mb-6">
                <p className="text-gray-600 mb-2">Current Balance</p>
                <p className="text-3xl font-bold text-green-600">₹{walletBalance.toFixed(2)}</p>
              </div>
              
              <div className="mb-6">
                <h3 className="font-medium mb-3">Add Money</h3>
                <div className="grid grid-cols-3 gap-3">
                  <button 
                    onClick={() => handleAddMoney(100)}
                    className="py-3 bg-gray-100 rounded-lg hover:bg-gray-200 font-medium"
                  >
                    ₹100
                  </button>
                  <button 
                    onClick={() => handleAddMoney(200)}
                    className="py-3 bg-gray-100 rounded-lg hover:bg-gray-200 font-medium"
                  >
                    ₹200
                  </button>
                  <button 
                    onClick={() => handleAddMoney(500)}
                    className="py-3 bg-gray-100 rounded-lg hover:bg-gray-200 font-medium"
                  >
                    ₹500
                  </button>
                </div>
              </div>
              
              <div className="mb-6">
                <h3 className="font-medium mb-3">Custom Amount</h3>
                <div className="flex space-x-2">
                  <input 
                    type="number" 
                    placeholder="Enter amount" 
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button 
                    onClick={(e) => {
                      const input = e.target.previousElementSibling;
                      const amount = parseFloat(input.value);
                      if (amount > 0) {
                        handleAddMoney(amount);
                        input.value = '';
                      }
                    }}
                    className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                  >
                    Add
                  </button>
                </div>
              </div>
              
              <div className="text-sm text-gray-500">
                <p>• Wallet balance can be used for ride payments</p>
                <p>• Minimum balance required: ₹0.00</p>
              </div>
            </div>
          </div>
        </div>
      )}
      
    </div>
  )
}