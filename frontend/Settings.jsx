import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'
import { 
  Settings as SettingsIcon, 
  Mail, 
  Key,
  TestTube,
  Save,
  CheckCircle,
  XCircle
} from 'lucide-react'

const Settings = () => {
  const [emailConfig, setEmailConfig] = useState({
    smtp_server: 'smtp.gmail.com',
    smtp_port: 587,
    use_tls: true,
    username: '',
    password: '',
    from_email: '',
    from_name: 'Website Design Specialist'
  })
  
  const [apiKeys, setApiKeys] = useState({
    apollo_api_key: '',
    builtwith_api_key: '',
    zerobounce_api_key: '',
    hunter_api_key: '',
    sendgrid_api_key: ''
  })
  
  const [testResults, setTestResults] = useState(null)
  const [testing, setTesting] = useState(false)
  const { toast } = useToast()

  const handleEmailConfigChange = (field, value) => {
    setEmailConfig(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleApiKeyChange = (field, value) => {
    setApiKeys(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const testEmailConfiguration = async () => {
    setTesting(true)
    try {
      const response = await fetch('/api/campaigns/test-email-config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          smtp_config: emailConfig,
          sendgrid_api_key: apiKeys.sendgrid_api_key
        })
      })

      const data = await response.json()
      setTestResults(data.test_result)
      
      if (data.success) {
        toast({
          title: "Success",
          description: "Email configuration test passed"
        })
      } else {
        toast({
          title: "Test Failed",
          description: data.test_result?.error || "Email configuration test failed",
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
      setTesting(false)
    }
  }

  const saveSettings = () => {
    // In a real application, you would save these to a backend
    localStorage.setItem('leadgen_email_config', JSON.stringify(emailConfig))
    localStorage.setItem('leadgen_api_keys', JSON.stringify(apiKeys))
    
    toast({
      title: "Success",
      description: "Settings saved successfully"
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">
          Configure your lead generation system
        </p>
      </div>

      <Tabs defaultValue="email" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="email">Email Configuration</TabsTrigger>
          <TabsTrigger value="apis">API Keys</TabsTrigger>
          <TabsTrigger value="templates">Email Templates</TabsTrigger>
        </TabsList>

        {/* Email Configuration */}
        <TabsContent value="email">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Mail className="h-5 w-5" />
                <span>Email Configuration</span>
              </CardTitle>
              <CardDescription>
                Configure SMTP settings for sending emails
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="smtp_server">SMTP Server</Label>
                  <Input
                    id="smtp_server"
                    value={emailConfig.smtp_server}
                    onChange={(e) => handleEmailConfigChange('smtp_server', e.target.value)}
                    placeholder="smtp.gmail.com"
                  />
                </div>
                
                <div>
                  <Label htmlFor="smtp_port">SMTP Port</Label>
                  <Input
                    id="smtp_port"
                    type="number"
                    value={emailConfig.smtp_port}
                    onChange={(e) => handleEmailConfigChange('smtp_port', parseInt(e.target.value))}
                    placeholder="587"
                  />
                </div>
                
                <div>
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    value={emailConfig.username}
                    onChange={(e) => handleEmailConfigChange('username', e.target.value)}
                    placeholder="your-email@gmail.com"
                  />
                </div>
                
                <div>
                  <Label htmlFor="password">Password / App Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={emailConfig.password}
                    onChange={(e) => handleEmailConfigChange('password', e.target.value)}
                    placeholder="Your app password"
                  />
                </div>
                
                <div>
                  <Label htmlFor="from_email">From Email</Label>
                  <Input
                    id="from_email"
                    value={emailConfig.from_email}
                    onChange={(e) => handleEmailConfigChange('from_email', e.target.value)}
                    placeholder="your-email@gmail.com"
                  />
                </div>
                
                <div>
                  <Label htmlFor="from_name">From Name</Label>
                  <Input
                    id="from_name"
                    value={emailConfig.from_name}
                    onChange={(e) => handleEmailConfigChange('from_name', e.target.value)}
                    placeholder="Website Design Specialist"
                  />
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Switch
                  checked={emailConfig.use_tls}
                  onCheckedChange={(checked) => handleEmailConfigChange('use_tls', checked)}
                />
                <Label>Use TLS/SSL</Label>
              </div>
              
              <div className="flex items-center space-x-4">
                <Button 
                  onClick={testEmailConfiguration}
                  disabled={testing}
                  variant="outline"
                  className="flex items-center space-x-2"
                >
                  {testing ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  ) : (
                    <TestTube className="h-4 w-4" />
                  )}
                  <span>Test Configuration</span>
                </Button>
                
                {testResults && (
                  <div className="flex items-center space-x-2">
                    {testResults.success ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-600" />
                    )}
                    <span className={`text-sm ${testResults.success ? 'text-green-600' : 'text-red-600'}`}>
                      {testResults.message || testResults.error}
                    </span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Keys */}
        <TabsContent value="apis">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Key className="h-5 w-5" />
                <span>API Keys</span>
              </CardTitle>
              <CardDescription>
                Configure API keys for data sources and services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="apollo_api_key">Apollo.io API Key</Label>
                  <Input
                    id="apollo_api_key"
                    type="password"
                    value={apiKeys.apollo_api_key}
                    onChange={(e) => handleApiKeyChange('apollo_api_key', e.target.value)}
                    placeholder="Enter Apollo.io API key"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    For finding companies and contacts
                  </p>
                </div>
                
                <div>
                  <Label htmlFor="builtwith_api_key">BuiltWith API Key</Label>
                  <Input
                    id="builtwith_api_key"
                    type="password"
                    value={apiKeys.builtwith_api_key}
                    onChange={(e) => handleApiKeyChange('builtwith_api_key', e.target.value)}
                    placeholder="Enter BuiltWith API key"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    For analyzing website technologies
                  </p>
                </div>
                
                <div>
                  <Label htmlFor="zerobounce_api_key">ZeroBounce API Key</Label>
                  <Input
                    id="zerobounce_api_key"
                    type="password"
                    value={apiKeys.zerobounce_api_key}
                    onChange={(e) => handleApiKeyChange('zerobounce_api_key', e.target.value)}
                    placeholder="Enter ZeroBounce API key"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    For email validation
                  </p>
                </div>
                
                <div>
                  <Label htmlFor="hunter_api_key">Hunter.io API Key</Label>
                  <Input
                    id="hunter_api_key"
                    type="password"
                    value={apiKeys.hunter_api_key}
                    onChange={(e) => handleApiKeyChange('hunter_api_key', e.target.value)}
                    placeholder="Enter Hunter.io API key"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    Alternative email validation service
                  </p>
                </div>
                
                <div>
                  <Label htmlFor="sendgrid_api_key">SendGrid API Key</Label>
                  <Input
                    id="sendgrid_api_key"
                    type="password"
                    value={apiKeys.sendgrid_api_key}
                    onChange={(e) => handleApiKeyChange('sendgrid_api_key', e.target.value)}
                    placeholder="Enter SendGrid API key"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    For sending emails via SendGrid (alternative to SMTP)
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Email Templates */}
        <TabsContent value="templates">
          <Card>
            <CardHeader>
              <CardTitle>Email Templates</CardTitle>
              <CardDescription>
                Customize your email templates for different triggers
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Template Variables</h4>
                  <div className="text-sm text-blue-800 space-y-1">
                    <p><code>{'{first_name}'}</code> - Contact's first name</p>
                    <p><code>{'{company_name}'}</code> - Company name</p>
                    <p><code>{'{company_domain}'}</code> - Company website</p>
                    <p><code>{'{industry}'}</code> - Company industry</p>
                    <p><code>{'{hiring_role}'}</code> - Role being hired (for hiring trigger)</p>
                    <p><code>{'{funding_stage}'}</code> - Funding stage (for funding trigger)</p>
                  </div>
                </div>
                
                <div className="text-center py-8 text-gray-500">
                  <SettingsIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>Template customization coming soon!</p>
                  <p className="text-sm">For now, templates are managed in the backend code.</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={saveSettings} className="flex items-center space-x-2">
          <Save className="h-4 w-4" />
          <span>Save Settings</span>
        </Button>
      </div>
    </div>
  )
}

export default Settings

