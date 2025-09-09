import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useToast } from '@/hooks/use-toast'
import { 
  Mail, 
  Send, 
  Eye,
  Users,
  Loader2,
  Plus,
  Edit,
  CheckCircle,
  AlertTriangle
} from 'lucide-react'

const EmailCampaigns = () => {
  const [contacts, setContacts] = useState([])
  const [selectedContacts, setSelectedContacts] = useState([])
  const [generatedEmails, setGeneratedEmails] = useState([])
  const [templates, setTemplates] = useState({})
  const [selectedTemplate, setSelectedTemplate] = useState('hiring')
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [previewEmail, setPreviewEmail] = useState(null)
  const [showPreview, setShowPreview] = useState(false)
  const [testMode, setTestMode] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    fetchContacts()
    fetchTemplates()
  }, [])

  const fetchContacts = async () => {
    try {
      const response = await fetch('/api/validation/filter-contacts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          min_decision_score: 0.5,
          email_validation_results: ['valid', 'risky']
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setContacts(data.contacts || [])
        }
      }
    } catch (error) {
      console.error('Error fetching contacts:', error)
    }
  }

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/campaigns/email-templates')
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setTemplates(data.templates || {})
        }
      }
    } catch (error) {
      console.error('Error fetching templates:', error)
    }
  }

  const generateEmails = async () => {
    if (selectedContacts.length === 0) {
      toast({
        title: "Error",
        description: "Please select contacts to generate emails for",
        variant: "destructive"
      })
      return
    }

    setIsGenerating(true)
    try {
      const response = await fetch('/api/campaigns/generate-emails', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contact_ids: selectedContacts,
          template_type: selectedTemplate
        })
      })

      const data = await response.json()
      
      if (data.success) {
        setGeneratedEmails(data.generated_emails || [])
        toast({
          title: "Success",
          description: `Generated ${data.total_generated} personalized emails`
        })
      } else {
        toast({
          title: "Error",
          description: data.error || "Failed to generate emails",
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
      setIsGenerating(false)
    }
  }

  const previewEmailForContact = async (contactId) => {
    try {
      const response = await fetch('/api/campaigns/preview-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contact_id: contactId,
          template_type: selectedTemplate
        })
      })

      const data = await response.json()
      
      if (data.success) {
        setPreviewEmail(data)
        setShowPreview(true)
      } else {
        toast({
          title: "Error",
          description: data.error || "Failed to generate preview",
          variant: "destructive"
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Network error occurred",
        variant: "destructive"
      })
    }
  }

  const sendEmails = async () => {
    if (generatedEmails.length === 0) {
      toast({
        title: "Error",
        description: "Please generate emails first",
        variant: "destructive"
      })
      return
    }

    setIsSending(true)
    try {
      // Prepare email data for sending
      const emailsToSend = generatedEmails.map(email => ({
        contact_id: email.contact_id,
        to_email: contacts.find(c => c.id === email.contact_id)?.email,
        subject: email.subject,
        body: email.body
      }))

      const response = await fetch('/api/campaigns/send-emails', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          emails: emailsToSend,
          test_mode: testMode
        })
      })

      const data = await response.json()
      
      if (data.success) {
        toast({
          title: "Success",
          description: testMode ? "Test completed successfully" : data.message
        })
        
        if (!testMode) {
          // Refresh contacts to show updated status
          fetchContacts()
          setGeneratedEmails([])
          setSelectedContacts([])
        }
      } else {
        toast({
          title: "Error",
          description: data.error || "Failed to send emails",
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
      setIsSending(false)
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
      setSelectedContacts(contacts.map(c => c.id))
    } else {
      setSelectedContacts([])
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Email Campaigns</h1>
          <p className="text-gray-600 mt-1">
            Generate and send personalized cold emails to your leads
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-2">
            <Checkbox
              checked={testMode}
              onCheckedChange={setTestMode}
            />
            <span className="text-sm">Test Mode</span>
          </div>
        </div>
      </div>

      {/* Campaign Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Mail className="h-5 w-5" />
            <span>Campaign Configuration</span>
          </CardTitle>
          <CardDescription>
            Select contacts and email template for your campaign
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Template Selection */}
          <div>
            <label className="text-sm font-medium mb-2 block">Email Template</label>
            <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(templates).map(([key, template]) => (
                  <SelectItem key={key} value={key}>
                    {template.name} - {template.description}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {templates[selectedTemplate] && (
              <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm font-medium">Preview:</p>
                <p className="text-sm text-gray-600 mt-1">{templates[selectedTemplate].preview}</p>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <Button 
              onClick={generateEmails}
              disabled={isGenerating || selectedContacts.length === 0}
              className="flex items-center space-x-2"
            >
              {isGenerating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Edit className="h-4 w-4" />
              )}
              <span>Generate Emails ({selectedContacts.length})</span>
            </Button>

            <Button 
              onClick={sendEmails}
              disabled={isSending || generatedEmails.length === 0}
              variant={testMode ? "outline" : "default"}
              className="flex items-center space-x-2"
            >
              {isSending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              <span>
                {testMode ? 'Test Send' : 'Send Emails'} ({generatedEmails.length})
              </span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Contact Selection */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>Select Contacts ({contacts.length})</span>
              </CardTitle>
              <CardDescription>
                Choose contacts for your email campaign
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                checked={selectedContacts.length === contacts.length && contacts.length > 0}
                onCheckedChange={handleSelectAll}
              />
              <span className="text-sm text-gray-600">Select All</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {contacts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No validated contacts available. Please validate contacts first.
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {contacts.map((contact) => (
                <div key={contact.id} className="flex items-center space-x-4 p-3 border rounded-lg hover:bg-gray-50">
                  <Checkbox
                    checked={selectedContacts.includes(contact.id)}
                    onCheckedChange={(checked) => handleSelectContact(contact.id, checked)}
                  />
                  
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium">
                          {contact.first_name} {contact.last_name}
                        </h4>
                        <p className="text-sm text-gray-600">{contact.job_title} at {contact.company_name}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">
                          {contact.trigger_type?.replace('_', ' ').toUpperCase()}
                        </Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => previewEmailForContact(contact.id)}
                          className="flex items-center space-x-1"
                        >
                          <Eye className="h-3 w-3" />
                          <span>Preview</span>
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Generated Emails */}
      {generatedEmails.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span>Generated Emails ({generatedEmails.length})</span>
            </CardTitle>
            <CardDescription>
              Review your personalized emails before sending
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {generatedEmails.map((email, index) => (
                <div key={index} className="p-4 border rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-medium">{email.contact_name}</h4>
                      <p className="text-sm text-gray-600">{email.company_name}</p>
                    </div>
                    <Badge className="bg-blue-500">
                      Score: {(email.personalization_score * 100 || 0).toFixed(0)}%
                    </Badge>
                  </div>
                  
                  <div className="space-y-2">
                    <div>
                      <span className="text-sm font-medium">Subject:</span>
                      <p className="text-sm text-gray-700">{email.subject}</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium">Preview:</span>
                      <p className="text-sm text-gray-700 line-clamp-3">
                        {email.body.substring(0, 200)}...
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Email Preview Dialog */}
      <Dialog open={showPreview} onOpenChange={setShowPreview}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Email Preview</DialogTitle>
            <DialogDescription>
              {previewEmail?.contact_info && (
                <>Preview for {previewEmail.contact_info.name} at {previewEmail.contact_info.company}</>
              )}
            </DialogDescription>
          </DialogHeader>
          
          {previewEmail && (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Subject:</label>
                <p className="text-sm bg-gray-50 p-2 rounded mt-1">{previewEmail.preview.subject}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium">Email Body:</label>
                <div className="text-sm bg-gray-50 p-4 rounded mt-1 whitespace-pre-wrap">
                  {previewEmail.preview.body}
                </div>
              </div>
              
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Template: {previewEmail.preview.template_type}</span>
                <span>Personalization: {(previewEmail.preview.personalization_score * 100 || 0).toFixed(0)}%</span>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Warning for Test Mode */}
      {testMode && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 text-yellow-800">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-medium">Test Mode Active</span>
            </div>
            <p className="text-sm text-yellow-700 mt-1">
              Emails will not actually be sent. This is for testing the email generation and preview functionality.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default EmailCampaigns

