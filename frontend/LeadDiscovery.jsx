import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/use-toast'
import { 
  Search, 
  Building2, 
  Users, 
  TrendingUp,
  Zap,
  Globe,
  Loader2,
  CheckCircle
} from 'lucide-react'

const LeadDiscovery = () => {
  const [triggerTypes, setTriggerTypes] = useState(['hiring', 'funding', 'outdated_tech'])
  const [limitPerType, setLimitPerType] = useState(20)
  const [isDiscovering, setIsDiscovering] = useState(false)
  const [discoveredCompanies, setDiscoveredCompanies] = useState([])
  const { toast } = useToast()

  const triggerOptions = [
    {
      id: 'hiring',
      label: 'Companies Hiring Marketers',
      description: 'Companies currently hiring marketing/sales professionals',
      icon: Users,
      color: 'bg-blue-500'
    },
    {
      id: 'funding',
      label: 'Recently Funded Companies',
      description: 'Startups that received funding in the last 30 days',
      icon: TrendingUp,
      color: 'bg-green-500'
    },
    {
      id: 'outdated_tech',
      label: 'Outdated Technology',
      description: 'Companies using outdated web technologies',
      icon: Globe,
      color: 'bg-orange-500'
    }
  ]

  const handleTriggerChange = (triggerId, checked) => {
    if (checked) {
      setTriggerTypes([...triggerTypes, triggerId])
    } else {
      setTriggerTypes(triggerTypes.filter(t => t !== triggerId))
    }
  }

  const discoverLeads = async () => {
    if (triggerTypes.length === 0) {
      toast({
        title: "Error",
        description: "Please select at least one trigger type",
        variant: "destructive"
      })
      return
    }

    setIsDiscovering(true)
    try {
      const response = await fetch('/api/leads/discover', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          trigger_types: triggerTypes,
          limit_per_type: limitPerType
        })
      })

      const data = await response.json()
      
      if (data.success) {
        setDiscoveredCompanies(data.companies || [])
        toast({
          title: "Success",
          description: data.message
        })
      } else {
        toast({
          title: "Error",
          description: data.error || "Failed to discover leads",
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
      setIsDiscovering(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Discover Leads</h1>
        <p className="text-gray-600 mt-1">
          Find potential clients based on specific triggers and signals
        </p>
      </div>

      {/* Discovery Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="h-5 w-5" />
            <span>Lead Discovery Configuration</span>
          </CardTitle>
          <CardDescription>
            Select the types of companies you want to target
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Trigger Types */}
          <div>
            <Label className="text-base font-medium">Trigger Types</Label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-3">
              {triggerOptions.map((option) => {
                const Icon = option.icon
                const isChecked = triggerTypes.includes(option.id)
                
                return (
                  <div
                    key={option.id}
                    className={`p-4 rounded-lg border-2 transition-all cursor-pointer ${
                      isChecked 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleTriggerChange(option.id, !isChecked)}
                  >
                    <div className="flex items-start space-x-3">
                      <Checkbox
                        checked={isChecked}
                        onChange={() => {}}
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <div className={`p-1 rounded ${option.color} text-white`}>
                            <Icon className="h-4 w-4" />
                          </div>
                          <h4 className="font-medium">{option.label}</h4>
                        </div>
                        <p className="text-sm text-gray-600">{option.description}</p>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Limit Per Type */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="limit">Companies per trigger type</Label>
              <Input
                id="limit"
                type="number"
                value={limitPerType}
                onChange={(e) => setLimitPerType(parseInt(e.target.value) || 20)}
                min="1"
                max="100"
                className="mt-1"
              />
              <p className="text-xs text-gray-600 mt-1">
                Maximum number of companies to discover for each selected trigger
              </p>
            </div>
          </div>

          {/* Discovery Button */}
          <div className="flex justify-end">
            <Button 
              onClick={discoverLeads}
              disabled={isDiscovering || triggerTypes.length === 0}
              className="flex items-center space-x-2"
            >
              {isDiscovering ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Zap className="h-4 w-4" />
              )}
              <span>
                {isDiscovering ? 'Discovering...' : 'Discover Leads'}
              </span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Discovery Results */}
      {discoveredCompanies.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span>Discovery Results</span>
            </CardTitle>
            <CardDescription>
              {discoveredCompanies.length} companies discovered and saved
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {discoveredCompanies.map((company, index) => (
                <div key={index} className="p-4 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <Building2 className="h-5 w-5 text-gray-600" />
                        <h4 className="font-medium text-lg">{company.name}</h4>
                        <Badge variant="outline">
                          {company.trigger_type?.replace('_', ' ').toUpperCase()}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div>
                          <span className="font-medium">Domain:</span> {company.domain}
                        </div>
                        <div>
                          <span className="font-medium">Industry:</span> {company.industry || 'N/A'}
                        </div>
                        <div>
                          <span className="font-medium">Employees:</span> {company.employee_count || 'N/A'}
                        </div>
                      </div>
                      
                      <div className="mt-2">
                        <span className="font-medium text-sm">Trigger:</span>
                        <span className="text-sm text-gray-600 ml-2">{company.trigger_details}</span>
                      </div>
                      
                      {company.contact_count > 0 && (
                        <div className="mt-2 flex items-center space-x-2">
                          <Users className="h-4 w-4 text-green-600" />
                          <span className="text-sm text-green-600 font-medium">
                            {company.contact_count} decision makers found
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tips */}
      <Card>
        <CardHeader>
          <CardTitle>Discovery Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm text-gray-600">
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <p><strong>Hiring Trigger:</strong> Companies hiring marketing roles are investing in growth and likely need website improvements.</p>
            </div>
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <p><strong>Funding Trigger:</strong> Recently funded companies have budget and need to upgrade their online presence.</p>
            </div>
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-orange-500 rounded-full mt-2"></div>
              <p><strong>Tech Trigger:</strong> Companies with outdated technology are prime candidates for website modernization.</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default LeadDiscovery

