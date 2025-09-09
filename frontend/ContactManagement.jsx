import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { useToast } from '@/hooks/use-toast'
import { 
  Users, 
  Building2, 
  Mail, 
  CheckCircle,
  XCircle,
  AlertCircle,
  Search,
  Filter,
  Loader2,
  Star
} from 'lucide-react'

const ContactManagement = () => {
  const [contacts, setContacts] = useState([])
  const [filteredContacts, setFilteredContacts] = useState([])
  const [selectedContacts, setSelectedContacts] = useState([])
  const [loading, setLoading] = useState(true)
  const [validating, setValidating] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [triggerFilter, setTriggerFilter] = useState('all')
  const [validationFilter, setValidationFilter] = useState('all')
  const { toast } = useToast()

  useEffect(() => {
    fetchContacts()
  }, [])

  useEffect(() => {
    filterContacts()
  }, [contacts, searchTerm, triggerFilter, validationFilter])

  const fetchContacts = async () => {
    try {
      const response = await fetch('/api/leads/companies?limit=100')
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          // Flatten contacts from all companies
          const allContacts = []
          data.companies.forEach(company => {
            company.top_contacts?.forEach(contact => {
              allContacts.push({
                ...contact,
                company_name: company.name,
                company_domain: company.domain,
                company_trigger: company.trigger_type,
                company_industry: company.industry
              })
            })
          })
          setContacts(allContacts)
        }
      }
    } catch (error) {
      console.error('Error fetching contacts:', error)
      toast({
        title: "Error",
        description: "Failed to fetch contacts",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const filterContacts = () => {
    let filtered = contacts

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(contact => 
        contact.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contact.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contact.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contact.company_name?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Trigger filter
    if (triggerFilter !== 'all') {
      filtered = filtered.filter(contact => contact.company_trigger === triggerFilter)
    }

    // Validation filter
    if (validationFilter !== 'all') {
      if (validationFilter === 'validated') {
        filtered = filtered.filter(contact => contact.email_validated)
      } else if (validationFilter === 'unvalidated') {
        filtered = filtered.filter(contact => !contact.email_validated)
      } else {
        filtered = filtered.filter(contact => contact.email_validation_result === validationFilter)
      }
    }

    // Sort by decision maker score
    filtered.sort((a, b) => (b.decision_maker_score || 0) - (a.decision_maker_score || 0))

    setFilteredContacts(filtered)
  }

  const validateSelectedContacts = async () => {
    if (selectedContacts.length === 0) {
      toast({
        title: "Error",
        description: "Please select contacts to validate",
        variant: "destructive"
      })
      return
    }

    setValidating(true)
    try {
      const response = await fetch('/api/validation/validate-contacts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contact_ids: selectedContacts
        })
      })

      const data = await response.json()
      
      if (data.success) {
        toast({
          title: "Success",
          description: data.message
        })
        fetchContacts() // Refresh the data
        setSelectedContacts([])
      } else {
        toast({
          title: "Error",
          description: data.error || "Failed to validate contacts",
          variant: "destructive"
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Network error occurred",
        variant: "destructive"
      })
    } finally {
      setValidating(false)
    }
  }

  const handleSelectContact = (contactId, checked) => {
    if (checked) {
      setSelectedContacts([...selectedContacts, contactId])
    } else {
      setSelectedContacts(selectedContacts.filter(id => id !== contactId))
    }
  }

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedContacts(filteredContacts.map(c => c.id))
    } else {
      setSelectedContacts([])
    }
  }

  const getValidationBadge = (contact) => {
    if (!contact.email_validated) {
      return <Badge variant="secondary">Unvalidated</Badge>
    }
    
    switch (contact.email_validation_result) {
      case 'valid':
        return <Badge className="bg-green-500"><CheckCircle className="h-3 w-3 mr-1" />Valid</Badge>
      case 'invalid':
        return <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" />Invalid</Badge>
      case 'risky':
        return <Badge className="bg-yellow-500"><AlertCircle className="h-3 w-3 mr-1" />Risky</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const getScoreStars = (score) => {
    const stars = Math.round((score || 0) * 5)
    return Array.from({ length: 5 }, (_, i) => (
      <Star 
        key={i} 
        className={`h-3 w-3 ${i < stars ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
      />
    ))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Contact Management</h1>
          <p className="text-gray-600 mt-1">
            Manage and validate your discovered contacts
          </p>
        </div>
        <Button 
          onClick={validateSelectedContacts}
          disabled={validating || selectedContacts.length === 0}
          className="flex items-center space-x-2"
        >
          {validating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <CheckCircle className="h-4 w-4" />
          )}
          <span>Validate Selected ({selectedContacts.length})</span>
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="h-5 w-5" />
            <span>Filters</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search contacts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Trigger Type</label>
              <Select value={triggerFilter} onValueChange={setTriggerFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Triggers</SelectItem>
                  <SelectItem value="hiring">Hiring</SelectItem>
                  <SelectItem value="funding">Funding</SelectItem>
                  <SelectItem value="outdated_tech">Outdated Tech</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-2 block">Email Status</label>
              <Select value={validationFilter} onValueChange={setValidationFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="validated">Validated</SelectItem>
                  <SelectItem value="unvalidated">Unvalidated</SelectItem>
                  <SelectItem value="valid">Valid</SelectItem>
                  <SelectItem value="invalid">Invalid</SelectItem>
                  <SelectItem value="risky">Risky</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-end">
              <Button variant="outline" onClick={() => {
                setSearchTerm('')
                setTriggerFilter('all')
                setValidationFilter('all')
              }}>
                Clear Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Contacts Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>Contacts ({filteredContacts.length})</span>
              </CardTitle>
              <CardDescription>
                Decision makers discovered from target companies
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                checked={selectedContacts.length === filteredContacts.length && filteredContacts.length > 0}
                onCheckedChange={handleSelectAll}
              />
              <span className="text-sm text-gray-600">Select All</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredContacts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No contacts found. Try adjusting your filters or discover new leads.
            </div>
          ) : (
            <div className="space-y-4">
              {filteredContacts.map((contact) => (
                <div key={contact.id} className="p-4 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-start space-x-4">
                    <Checkbox
                      checked={selectedContacts.includes(contact.id)}
                      onCheckedChange={(checked) => handleSelectContact(contact.id, checked)}
                      className="mt-1"
                    />
                    
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h4 className="font-medium text-lg">
                            {contact.first_name} {contact.last_name}
                          </h4>
                          <p className="text-gray-600">{contact.job_title}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          {getValidationBadge(contact)}
                          <Badge variant="outline">
                            {contact.company_trigger?.replace('_', ' ').toUpperCase()}
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div className="flex items-center space-x-2">
                          <Mail className="h-4 w-4 text-gray-400" />
                          <span>{contact.email}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Building2 className="h-4 w-4 text-gray-400" />
                          <span>{contact.company_name}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-gray-600">Decision Score:</span>
                          <div className="flex items-center space-x-1">
                            {getScoreStars(contact.decision_maker_score)}
                            <span className="text-xs text-gray-500 ml-1">
                              ({(contact.decision_maker_score * 100 || 0).toFixed(0)}%)
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      {contact.contacted && (
                        <div className="mt-2 flex items-center space-x-2 text-sm text-green-600">
                          <CheckCircle className="h-4 w-4" />
                          <span>Contacted on {new Date(contact.contact_date).toLocaleDateString()}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default ContactManagement

