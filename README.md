# AI Civic Complaint Chat App

A modern, AI-powered web application designed to streamline the process of filing civic complaints for citizens. Built with React, this application provides an intuitive chat-based interface for reporting urban issues and connecting with city authorities.

## 🚀 Features

### Core Functionality
- **AI-Powered Chat Interface**: Interactive chatbot that guides users through the complaint filing process
- **Category-Based Complaint System**: Pre-defined categories for different types of civic issues:
  - Road & Traffic Issues (potholes, traffic signals, road damage)
  - Electricity/Power Problems (power outages, electrical issues)
  - Water & Plumbing Issues (leaks, supply problems, drainage)
  - Garbage & Waste Collection (collection delays, overflowing bins)

### User Experience
- **Step-by-Step Guidance**: Clear, sequential form completion process
- **Mobile-First Design**: Responsive layout that works perfectly on all devices
- **Real-Time Validation**: Immediate feedback for form inputs and data validation
- **Intuitive Navigation**: Easy-to-use interface with visual cues and clear instructions

### Technical Features
- **Progressive Web App**: Modern web technologies for fast, reliable performance
- **Secure Data Handling**: Proper validation and sanitization of user inputs
- **Real-Time Communication**: Seamless API integration for complaint submission
- **Cross-Platform Compatibility**: Works on desktop, tablet, and mobile devices

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern React with hooks and functional components
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework for responsive design
- **React Router** - Client-side routing (if needed)

### Backend
- **FastAPI** - High-performance Python web framework
- **Python 3.11+** - Modern Python runtime
- **Supabase** - PostgreSQL database with real-time capabilities

### Development Tools
- **ESLint** - Code linting and quality assurance
- **Prettier** - Code formatting
- **Git** - Version control
- **npm/yarn** - Package management

## 📁 Project Structure

```
/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── App.jsx          # Main application component
│   │   ├── index.css        # Global styles and Tailwind imports
│   │   ├── main.jsx         # Application entry point
│   │   └── components/      # Reusable React components
│   ├── public/              # Static assets
│   ├── package.json         # Frontend dependencies
│   └── vite.config.js       # Vite configuration
├── backend/                 # FastAPI backend application
│   ├── main.py              # Main FastAPI application
│   ├── database.py          # Database connection and utilities
│   ├── requirements.txt     # Python dependencies
│   └── supabase_schema.sql  # Database schema
└── README.md                # Project documentation
```

## 🎯 Key Components

### Frontend Components
- **Header**: Fixed navigation with branding and new complaint button
- **Category Selection**: Interactive category cards for issue type selection
- **Chat Interface**: Message-based conversation flow
- **Form Steps**: Sequential data collection (description, location, contact info)
- **Success/Error States**: Clear feedback for user actions

### Backend Services
- **Chat API**: AI-powered conversation handling
- **Complaint Submission**: Secure complaint data processing
- **Database Integration**: Supabase PostgreSQL operations
- **Validation Services**: Input sanitization and business logic

## 🔄 Workflow

1. **Category Selection**: User selects the type of complaint from predefined categories
2. **AI-Guided Conversation**: Chatbot collects complaint details step-by-step:
   - Issue description
   - Location details
   - Personal information (name, mobile, email)
3. **Data Validation**: Real-time validation ensures data quality
4. **Complaint Submission**: Secure submission to city authorities database
5. **Confirmation**: User receives confirmation and tracking information

## 📱 Mobile Optimization

The application is specifically optimized for mobile devices with:
- **Vertical Header Layout**: Stacked logo/title and button for mobile screens
- **Touch-Friendly Interface**: Large tap targets and gesture support
- **Responsive Typography**: Readable text sizes across all screen sizes
- **Optimized Spacing**: Proper padding and margins for mobile viewing
- **Performance**: Fast loading and smooth interactions on mobile networks

## 🗄️ Database Schema

The application uses Supabase with the following main entities:
- **Complaints Table**: Stores all submitted complaints with metadata
- **Categories Table**: Predefined complaint categories
- **Users Table**: Citizen information and contact details
- **Audit Logs**: Track all system interactions for transparency

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ashishjha1304/AI-Civic-Complaint-Chat-App.git
   cd AI-Civic-Complaint-Chat-App
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   # Configure Supabase credentials
   python main.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Environment Configuration**
   - Set up Supabase project
   - Configure API endpoints
   - Set environment variables

## 🎨 Design Philosophy

- **Accessibility First**: WCAG compliant design for all users
- **Progressive Enhancement**: Works without JavaScript, enhanced with it
- **Performance Focused**: Optimized for fast loading and smooth interactions
- **Inclusive Design**: Works for users with different abilities and device types
- **Trust Building**: Transparent processes and clear communication

## 📈 Future Enhancements

- **Multi-language Support**: Localization for different regions
- **Offline Capability**: Service worker for offline complaint drafting
- **Photo Attachments**: Visual evidence upload functionality
- **Status Tracking**: Real-time complaint progress updates
- **Analytics Dashboard**: City administration insights

## 🤝 Contributing

This project aims to improve civic engagement and government-citizen communication. Contributions are welcome for:
- UI/UX improvements
- Accessibility enhancements
- Performance optimizations
- Feature additions
- Bug fixes

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For technical support or feature requests, please create an issue in the GitHub repository.

---

**Built with ❤️ for better civic engagement and responsive governance.**