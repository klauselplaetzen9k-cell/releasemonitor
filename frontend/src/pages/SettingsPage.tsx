import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { ThemeToggle } from '../hooks/useTheme'

export default function SettingsPage() {
  const { user } = useAuth()
  const [formData, setFormData] = useState({
    firstName: user?.first_name || '',
    lastName: user?.last_name || '',
    email: user?.email || '',
  })
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    // TODO: Implement settings update
    setTimeout(() => {
      setSaving(false)
      setMessage('Settings saved!')
      setTimeout(() => setMessage(''), 3000)
    }, 1000)
  }

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">Settings</h1>
          <p className="page-subtitle">Manage your account and preferences</p>
        </div>
        <ThemeToggle />
      </div>

      <div className="card">
        <h2 className="card-title" style={{ marginBottom: '1.5rem' }}>Profile</h2>
        
        {message && (
          <div className="badge badge-success" style={{ width: '100%', marginBottom: '1rem', textAlign: 'center' }}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">First Name</label>
              <input
                type="text"
                className="form-input"
                value={formData.firstName}
                onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Last Name</label>
              <input
                type="text"
                className="form-input"
                value={formData.lastName}
                onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-input"
              value={formData.email}
              disabled
              style={{ background: 'var(--background)' }}
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={saving} style={{ width: 'auto' }}>
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>

      <div className="card">
        <h2 className="card-title" style={{ marginBottom: '1.5rem' }}>Appearance</h2>
        
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <p style={{ fontWeight: 500 }}>Dark Mode</p>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
              Toggle between light and dark theme
            </p>
          </div>
          <ThemeToggle />
        </div>
      </div>

      <div className="card">
        <h2 className="card-title" style={{ marginBottom: '1.5rem' }}>Notifications</h2>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
            <input type="checkbox" defaultChecked />
            <span>Email notifications for new releases</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
            <input type="checkbox" />
            <span>Email notifications for pre-releases</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }}>
            <input type="checkbox" defaultChecked />
            <span>Weekly digest email</span>
          </label>
        </div>
      </div>

      <div className="card" style={{ borderColor: 'var(--error)' }}>
        <h2 className="card-title" style={{ color: 'var(--error)', marginBottom: '1rem' }}>Danger Zone</h2>
        
        <button
          className="btn"
          style={{ background: 'var(--error)', color: 'white' }}
          onClick={() => {
            if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
              // TODO: Implement account deletion
              alert('Account deletion not yet implemented')
            }
          }}
        >
          Delete Account
        </button>
      </div>
    </div>
  )
}
