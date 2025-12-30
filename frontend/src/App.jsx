import { useState, useRef, useEffect } from 'react'

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m here to help you file a complaint. Please select the type of issue you want to report by clicking one of the buttons below:'
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [showCategorySelection, setShowCategorySelection] = useState(true)
  const [complaintCompleted, setComplaintCompleted] = useState(false)

  // Form state for step-by-step input
  const [currentStep, setCurrentStep] = useState(null)
  const [formData, setFormData] = useState({
    description: '',
    location: '',
    name: '',
    email: '',
    phone: ''
  })

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Generate unique session ID for this conversation
  const sessionId = useRef(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Check if complaint is completed
  useEffect(() => {
    const lastMessage = messages[messages.length - 1]
    if (lastMessage && lastMessage.role === 'assistant') {
      const successMessage = "Thank you! Your complaint has been recorded and submitted. We will look into this issue and get back to you soon."
      if (lastMessage.content.includes(successMessage) || 
          lastMessage.content.toLowerCase().includes("thank you") && 
          lastMessage.content.toLowerCase().includes("recorded and submitted")) {
        setComplaintCompleted(true)
        setShowCategorySelection(false)
        setCurrentStep(null)
      }
    }
  }, [messages])

  useEffect(() => {
    if (!showCategorySelection && inputRef.current) {
      inputRef.current.focus()
    }
  }, [showCategorySelection])

  const resetComplaint = async () => {
    try {
      await fetch('http://localhost:8000/reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      setMessages([
        {
          role: 'assistant',
          content: 'Hello! I\'m here to help you file a new complaint. Please select the type of issue you want to report by clicking one of the buttons below:'
        }
      ])
      setShowCategorySelection(true)
      setCurrentStep(null)
      setComplaintCompleted(false)
      setFormData({
        description: '',
        location: '',
        name: '',
        email: '',
        phone: ''
      })
      setInput('')
      sessionId.current = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    } catch (error) {
      console.error('Error resetting:', error)
      setMessages([
        {
          role: 'assistant',
          content: 'Hello! I\'m here to help you file a new complaint. Please select the type of issue you want to report by clicking one of the buttons below:'
        }
      ])
      setShowCategorySelection(true)
      setCurrentStep(null)
      setComplaintCompleted(false)
      setFormData({
        description: '',
        location: '',
        name: '',
        email: '',
        phone: ''
      })
      setInput('')
      sessionId.current = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    }
  }

  const handleCategorySelect = async (category) => {
    if (loading) return

    setLoading(true)
    setMessages(prev => [...prev, { role: 'user', content: category }])

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: category,
          session_id: sessionId.current
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
      setShowCategorySelection(false)
      setCurrentStep('description')
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again or start a new complaint.'
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleFormSubmit = async (field, value) => {
    if (loading || (field !== 'contact' && !value.trim())) return

    setLoading(true)

    const fieldLabels = {
      description: 'Brief explanation',
      location: 'Location',
      name: 'Name',
      email: 'Email',
      phone: 'Phone'
    }

    setMessages(prev => [...prev, {
      role: 'user',
      content: `${fieldLabels[field]}: ${value}`
    }])

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: value,
          session_id: sessionId.current
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])

      const steps = ['description', 'location', 'name']
      const currentIndex = steps.indexOf(currentStep)
      if (currentIndex < steps.length - 1) {
        setCurrentStep(steps[currentIndex + 1])
      } else {
        setCurrentStep(null)
      }

      setFormData(prev => ({ ...prev, [field]: '' }))
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }])
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setShowCategorySelection(false)
    setLoading(true)

    setMessages(prev => [...prev, { role: 'user', content: userMessage }])

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId.current
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again or start a new complaint.'
      }])
    } finally {
      setLoading(false)
      setTimeout(() => {
        inputRef.current?.focus()
      }, 100)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const categories = [
    {
      id: 'road',
      title: 'Road & Traffic Issues',
      description: 'Potholes, traffic signals, road damage',
      icon: '🛣️',
      value: 'road/traffic issues',
      gradient: 'from-blue-500 via-blue-600 to-cyan-500',
      hoverGradient: 'from-blue-600 via-blue-700 to-cyan-600',
      iconBg: 'bg-gradient-to-br from-blue-400 to-cyan-500'
    },
    {
      id: 'electricity',
      title: 'Electricity / Power Problems',
      description: 'Power outages, electrical issues',
      icon: '⚡',
      value: 'electricity/power problems',
      gradient: 'from-amber-500 via-orange-500 to-yellow-500',
      hoverGradient: 'from-amber-600 via-orange-600 to-yellow-600',
      iconBg: 'bg-gradient-to-br from-amber-400 to-orange-500'
    },
    {
      id: 'water',
      title: 'Water & Plumbing Issues',
      description: 'Leaks, supply problems, drainage',
      icon: '💧',
      value: 'water/plumbing issues',
      gradient: 'from-cyan-500 via-blue-500 to-teal-500',
      hoverGradient: 'from-cyan-600 via-blue-600 to-teal-600',
      iconBg: 'bg-gradient-to-br from-cyan-400 to-blue-500'
    },
    {
      id: 'garbage',
      title: 'Garbage & Waste Collection',
      description: 'Collection delays, overflowing bins',
      icon: '🗑️',
      value: 'garbage/waste collection',
      gradient: 'from-emerald-500 via-teal-500 to-green-500',
      hoverGradient: 'from-emerald-600 via-teal-600 to-green-600',
      iconBg: 'bg-gradient-to-br from-emerald-400 to-teal-500'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Fixed Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200/50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl blur-sm opacity-50"></div>
                <div className="relative w-14 h-14 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                  <span className="text-2xl">🏙️</span>
                </div>
              </div>
            <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                  Smart City Complaint Assistant
                </h1>
                <p className="text-sm text-gray-600 mt-1 font-medium">Your voice matters. Report issues easily.</p>
              </div>
            </div>
            <button
              onClick={resetComplaint}
              className="group relative px-5 py-2.5 rounded-xl bg-white border border-gray-200 text-gray-700 text-sm font-semibold hover:bg-gray-50 hover:border-gray-300 hover:shadow-md transition-all duration-300 flex items-center gap-2 overflow-hidden"
            >
              <span className="relative z-10 flex items-center gap-2">
                <span className="text-lg">➕</span>
                <span>New Complaint</span>
              </span>
              <span className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-24 sm:pt-28 pb-6 sm:pb-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          {/* Chat Container */}
          <div className="bg-white/70 backdrop-blur-2xl rounded-2xl sm:rounded-3xl shadow-2xl border border-white/50 overflow-hidden relative">
            {/* Subtle corner accent */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-indigo-100/20 to-purple-100/20 rounded-bl-full pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-blue-100/20 to-cyan-100/20 rounded-tr-full pointer-events-none"></div>
            {/* Messages Area */}
            <div className="h-[calc(100vh-280px)] sm:h-[calc(100vh-300px)] lg:h-[calc(100vh-320px)] min-h-[400px] sm:min-h-[500px] overflow-y-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 space-y-3 sm:space-y-4 bg-gradient-to-b from-white/60 via-gray-50/40 to-white/30 relative">
              {/* Subtle pattern overlay */}
              <div className="absolute inset-0 opacity-[0.02] pointer-events-none" style={{
                backgroundImage: `radial-gradient(circle at 2px 2px, rgb(99, 102, 241) 1px, transparent 0)`,
                backgroundSize: '40px 40px'
              }}></div>
              
          {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex gap-3 sm:gap-4 animate-fade-in ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="relative flex-shrink-0">
                      <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full blur-md opacity-30"></div>
                      <div className="relative w-10 h-10 sm:w-11 sm:h-11 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                        <span className="text-white text-base sm:text-lg">🤖</span>
                      </div>
                    </div>
                  )}
                  <div
                    className={`max-w-[85%] sm:max-w-[78%] rounded-2xl px-4 sm:px-5 py-3 sm:py-4 shadow-lg ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-br from-indigo-500 via-purple-600 to-indigo-600 text-white rounded-br-md shadow-indigo-500/30'
                        : msg.content.toLowerCase().includes("thank you") && msg.content.toLowerCase().includes("recorded and submitted")
                        ? 'bg-gradient-to-br from-emerald-50 to-teal-50 border-2 border-emerald-200/50 rounded-bl-md shadow-emerald-200/30'
                        : 'bg-white/95 text-gray-800 border border-gray-100/50 rounded-bl-md shadow-gray-200/50'
                    } ${idx === 0 && msg.role === 'assistant' ? 'ring-2 ring-indigo-200/50' : ''}`}
                  >
                    {msg.content.toLowerCase().includes("thank you") && msg.content.toLowerCase().includes("recorded and submitted") ? (
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center mt-0.5">
                          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
              </div>
                        <div className="flex-1">
                          <p className="text-sm sm:text-base leading-relaxed font-medium text-gray-800 break-words whitespace-pre-wrap">
                {msg.content}
                          </p>
                        </div>
                      </div>
                    ) : (
                      <p className={`whitespace-pre-wrap font-medium break-words ${
                        idx === 0 && msg.role === 'assistant' 
                          ? 'text-base sm:text-lg leading-relaxed sm:leading-loose' 
                          : 'text-sm leading-relaxed'
                      }`}>{msg.content}</p>
                    )}
                  </div>
                  {msg.role === 'user' && (
                    <div className="relative flex-shrink-0">
                      <div className="absolute inset-0 bg-gradient-to-br from-gray-400 to-gray-600 rounded-full blur-md opacity-30"></div>
                      <div className="relative w-10 h-10 sm:w-11 sm:h-11 rounded-full bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center shadow-lg">
                        <span className="text-white text-base sm:text-lg">👤</span>
              </div>
                    </div>
                  )}
            </div>
          ))}
              
              {/* Helper card when few messages and category selection is visible */}
              {messages.length <= 2 && showCategorySelection && !loading && (
                <div className="flex justify-center pt-4 pb-2">
                  <div className="bg-gradient-to-br from-indigo-50/80 to-purple-50/80 backdrop-blur-sm rounded-xl px-5 py-4 border border-indigo-100/50 shadow-sm max-w-md">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center">
                        <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-gray-700 leading-relaxed">
                          <span className="text-indigo-600 font-semibold">Quick tip:</span> Select a category below to start filing your complaint. Our system will guide you through each step.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
          {loading && (
                <div className="flex gap-3 sm:gap-4 justify-start animate-fade-in">
                  <div className="relative flex-shrink-0">
                    <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full blur-md opacity-30"></div>
                    <div className="relative w-10 h-10 sm:w-11 sm:h-11 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                      <span className="text-white text-base sm:text-lg">🤖</span>
                    </div>
                  </div>
                  <div className="bg-white/95 rounded-2xl rounded-bl-md px-4 sm:px-5 py-3 sm:py-4 shadow-lg border border-gray-100/50">
                    <div className="flex gap-2">
                      <div className="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
              
              {/* Success completion indicator */}
              {complaintCompleted && (
                <div className="flex justify-center pt-4 pb-2 animate-fade-in">
                  <div className="bg-gradient-to-br from-emerald-50/90 to-teal-50/90 backdrop-blur-sm rounded-xl px-5 py-4 border-2 border-emerald-200/50 shadow-md max-w-md">
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-800 mb-1">Complaint Successfully Submitted</p>
                        <p className="text-xs text-gray-600 leading-relaxed">This conversation has ended. You can start a new complaint if needed.</p>
                      </div>
                    </div>
                  </div>
        </div>
              )}
            </div>

            {/* Category Selection */}
            {showCategorySelection && !complaintCompleted && (
              <div className="px-4 sm:px-6 lg:px-8 py-6 sm:py-8 bg-gradient-to-b from-white/50 via-indigo-50/20 to-gray-50/30 border-t border-indigo-100/30 relative overflow-hidden">
                {/* Subtle gradient accent */}
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-indigo-200/50 to-transparent"></div>
                
                <div className="mb-6 sm:mb-8 text-center relative z-10">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-100 to-purple-100 mb-4 shadow-lg">
                    <span className="text-3xl">👆</span>
                  </div>
                  <p className="text-base font-semibold text-gray-900 mb-2">
                    Select a category to begin filing your complaint
                  </p>
                  <p className="text-sm text-gray-600">This helps us route your complaint to the right department quickly</p>
                </div>
                
                {/* Visual divider */}
                <div className="flex items-center justify-center mb-6 sm:mb-8 relative z-10">
                  <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent"></div>
                  <div className="mx-4 w-2 h-2 rounded-full bg-indigo-200"></div>
                  <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent"></div>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 relative z-10">
                  {categories.map((category) => (
              <button
                      key={category.id}
                      onClick={() => handleCategorySelect(category.value)}
                disabled={loading}
                      className="group relative overflow-hidden bg-white/90 backdrop-blur-sm rounded-2xl p-6 text-left hover:shadow-2xl transition-all duration-500 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed border border-gray-200/50 hover:border-transparent"
                    >
                      {/* Animated gradient background on hover */}
                      <div className={`absolute inset-0 bg-gradient-to-br ${category.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`}></div>
                      
                      {/* Content */}
                      <div className="relative z-10 flex items-start gap-5">
                        <div className={`relative flex-shrink-0 ${category.iconBg} w-16 h-16 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                          <div className="absolute inset-0 bg-white/20 rounded-xl"></div>
                          <span className="relative text-3xl">{category.icon}</span>
                        </div>
                        <div className="flex-1 min-w-0 pt-1">
                          <h3 className="font-bold text-gray-900 mb-2 text-base group-hover:text-white transition-colors duration-300">
                            {category.title}
                          </h3>
                          <p className="text-sm text-gray-600 leading-relaxed group-hover:text-white/90 transition-colors duration-300">
                            {category.description}
                          </p>
                        </div>
                        {/* Arrow indicator */}
                        <div className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-x-2 group-hover:translate-x-0">
                          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </div>
              </button>
                  ))}
                </div>
              </div>
            )}

            {/* Form Steps */}
            {!showCategorySelection && currentStep && !complaintCompleted && (
              <div className="px-4 sm:px-6 lg:px-8 py-6 sm:py-8 bg-gradient-to-b from-white/50 via-indigo-50/20 to-gray-50/30 border-t border-indigo-100/30 relative overflow-hidden">
                {/* Subtle gradient accent */}
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-indigo-200/50 to-transparent"></div>
                
                <div className="max-w-2xl mx-auto animate-slide-up relative z-10">
                  {currentStep === 'description' && (
                    <div className="space-y-4 sm:space-y-6">
                      <div className="text-center mb-6 sm:mb-8">
                        <div className="relative inline-block mb-4">
                          <div className="absolute inset-0 bg-indigo-200 rounded-full blur-xl opacity-50"></div>
                          <div className="relative inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-100 to-purple-100 shadow-lg">
                            <span className="text-3xl">📝</span>
                          </div>
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900 mb-2">Brief Explanation</h3>
                        <p className="text-sm text-gray-600 font-medium">Please describe the problem (at least 10 characters)</p>
                      </div>
                      <textarea
                        value={formData.description}
                        onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                        placeholder="e.g., There is a large pothole causing damage to vehicles..."
                        disabled={loading}
                        rows="5"
                        className="w-full px-5 py-4 rounded-2xl border-2 border-gray-200 bg-white/90 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-300 resize-none shadow-sm hover:shadow-md"
                      />
              <button
                        onClick={() => handleFormSubmit('description', formData.description)}
                        disabled={loading || formData.description.length < 10}
                        className="group relative w-full px-8 py-4 rounded-2xl bg-gradient-to-r from-indigo-500 via-purple-600 to-indigo-600 text-white font-semibold shadow-xl hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:scale-[1.02] overflow-hidden"
              >
                        <span className="relative z-10 flex items-center justify-center gap-2">
                          <span>Continue to Location</span>
                          <svg className="w-5 h-5 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                          </svg>
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 via-purple-700 to-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </button>
                    </div>
                  )}

                  {currentStep === 'location' && (
                    <div className="space-y-4 sm:space-y-6">
                      <div className="text-center mb-6 sm:mb-8">
                        <div className="relative inline-block mb-4">
                          <div className="absolute inset-0 bg-cyan-200 rounded-full blur-xl opacity-50"></div>
                          <div className="relative inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-100 to-blue-100 shadow-lg">
                            <span className="text-3xl">📍</span>
                          </div>
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900 mb-2">Location</h3>
                        <p className="text-sm text-gray-600 font-medium">Where is this issue located? (at least 3 characters)</p>
                      </div>
                      <input
                        type="text"
                        value={formData.location}
                        onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                        placeholder="e.g., 123 Main Street or Downtown Area"
                        disabled={loading}
                        className="w-full px-5 py-4 rounded-2xl border-2 border-gray-200 bg-white/90 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-300 shadow-sm hover:shadow-md"
                      />
              <button
                        onClick={() => handleFormSubmit('location', formData.location)}
                        disabled={loading || formData.location.length < 3}
                        className="group relative w-full px-8 py-4 rounded-2xl bg-gradient-to-r from-indigo-500 via-purple-600 to-indigo-600 text-white font-semibold shadow-xl hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:scale-[1.02] overflow-hidden"
              >
                        <span className="relative z-10 flex items-center justify-center gap-2">
                          <span>Continue to Your Name</span>
                          <svg className="w-5 h-5 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                          </svg>
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 via-purple-700 to-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </button>
                    </div>
                  )}

                  {currentStep === 'name' && (
                    <div className="space-y-4 sm:space-y-6">
                      <div className="text-center mb-6 sm:mb-8">
                        <div className="relative inline-block mb-4">
                          <div className="absolute inset-0 bg-purple-200 rounded-full blur-xl opacity-50"></div>
                          <div className="relative inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-100 to-pink-100 shadow-lg">
                            <span className="text-3xl">👤</span>
                          </div>
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900 mb-2">Your Name</h3>
                        <p className="text-sm text-gray-600 font-medium">What is your full name? (at least 2 characters)</p>
                      </div>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                        placeholder="e.g., John Smith"
                        disabled={loading}
                        className="w-full px-5 py-4 rounded-2xl border-2 border-gray-200 bg-white/90 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-300 shadow-sm hover:shadow-md"
                      />
              <button
                        onClick={() => handleFormSubmit('name', formData.name)}
                        disabled={loading || formData.name.length < 2}
                        className="group relative w-full px-8 py-4 rounded-2xl bg-gradient-to-r from-indigo-500 via-purple-600 to-indigo-600 text-white font-semibold shadow-xl hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:scale-[1.02] overflow-hidden"
              >
                        <span className="relative z-10 flex items-center justify-center gap-2">
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span>Submit Complaint</span>
                        </span>
                        <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 via-purple-700 to-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </button>
                    </div>
                  )}
            </div>
          </div>
        )}

            {/* Text Input (fallback) */}
            {!showCategorySelection && !currentStep && !complaintCompleted && (
              <div className="px-4 sm:px-6 lg:px-8 py-4 sm:py-6 bg-gradient-to-b from-white/50 via-indigo-50/20 to-gray-50/30 border-t border-indigo-100/30 relative overflow-hidden">
                {/* Subtle gradient accent */}
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-indigo-200/50 to-transparent"></div>
                
                {/* Helper text when waiting for input */}
                <div className="mb-4 text-center">
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-50/80 border border-indigo-100/50">
                    <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                    <p className="text-xs font-medium text-gray-700">Type your response below</p>
                  </div>
                </div>
                
                <div className="flex gap-3 sm:gap-4 relative z-10">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your response here..."
            disabled={loading}
                    className="flex-1 px-5 py-4 rounded-2xl border-2 border-gray-200 bg-white/90 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-300 shadow-sm hover:shadow-md"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
                    className="group relative px-8 py-4 rounded-2xl bg-gradient-to-r from-indigo-500 via-purple-600 to-indigo-600 text-white font-semibold shadow-xl hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:scale-[1.02] overflow-hidden"
          >
                    <span className="relative z-10 flex items-center gap-2">
                      <span>Send</span>
                      <svg className="w-5 h-5 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    </span>
                    <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 via-purple-700 to-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  </button>
                </div>
              </div>
            )}

            {/* Complaint Completed - End State */}
            {complaintCompleted && (
              <div className="px-4 sm:px-6 lg:px-8 py-6 sm:py-8 bg-gradient-to-b from-emerald-50/30 via-teal-50/20 to-white/30 border-t border-emerald-200/30 relative overflow-hidden">
                {/* Subtle gradient accent */}
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-emerald-300/50 to-transparent"></div>
                
                <div className="max-w-md mx-auto text-center space-y-4 relative z-10">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-100 to-teal-100 mb-2 shadow-lg">
                    <svg className="w-8 h-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-sm font-medium text-gray-700">Your complaint has been successfully submitted</p>
                  <button
                    onClick={resetComplaint}
                    className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-600 to-indigo-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02]"
                  >
                    <span>➕</span>
                    <span>Start New Complaint</span>
          </button>
                </div>
        </div>
        )}
      </div>
        </div>
      </main>
    </div>
  )
}

export default App
