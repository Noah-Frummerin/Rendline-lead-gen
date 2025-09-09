import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import Navbar from './components/Navbar'
import Dashboard from './components/Dashboard'
import LeadDiscovery from './components/LeadDiscovery'
import ContactManagement from './components/ContactManagement'
import EmailCampaigns from './components/EmailCampaigns'
import Settings from './components/Settings'
import './App.css'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/discover" element={<LeadDiscovery />} />
            <Route path="/contacts" element={<ContactManagement />} />
            <Route path="/campaigns" element={<EmailCampaigns />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
        <Toaster />
      </div>
    </Router>
  )
}

export default App

