import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { releasesApi, subscriptionsApi } from '../api/axios'
import { formatDistanceToNow } from 'date-fns'

interface Release {
  id: number
  project_name: string
  project_source: string
  project_avatar_url: string | null
  version: string
  release_date: string | null
  changelog: string | null
  tag_name: string | null
  prerelease: boolean
}

export default function DashboardPage() {
  const [releases, setReleases] = useState<Release[]>([])
  const [stats, setStats] = useState({ projects: 0, releases: 0, subscribed: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboard()
  }, [])

  const fetchDashboard = async () => {
    try {
      const [feedRes, subsRes] = await Promise.all([
        releasesApi.feed({ limit: 10, days: 7 }),
        subscriptionsApi.list(),
      ])
      
      setReleases(feedRes.data)
      setStats({
        projects: 0, // TODO: Fetch total
        releases: feedRes.data.length,
        subscribed: subsRes.data.length,
      })
    } catch (error) {
      console.error('Failed to fetch dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading dashboard...</div>
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Your release monitoring overview</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.projects}</div>
          <div className="stat-label">Monitored Projects</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.releases}</div>
          <div className="stat-label">Releases This Week</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.subscribed}</div>
          <div className="stat-label">Subscriptions</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recent Releases</h2>
          <Link to="/projects" className="btn btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}>
            View All
          </Link>
        </div>

        {releases.length > 0 ? (
          <div className="release-list">
            {releases.map((release) => (
              <div key={release.id} className="release-item">
                <div className="release-icon">
                  {release.project_name.charAt(0).toUpperCase()}
                </div>
                <div className="release-content">
                  <div className="release-title">
                    {release.project_name}
                    {release.prerelease && (
                      <span className="badge badge-warning" style={{ marginLeft: '0.5rem' }}>
                        Pre-release
                      </span>
                    )}
                  </div>
                  <div className="release-version">Version {release.version}</div>
                  {release.release_date && (
                    <div className="release-date">
                      {formatDistanceToNow(new Date(release.release_date), { addSuffix: true })}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">📦</div>
            <h3>No releases yet</h3>
            <p>Subscribe to some projects to see their releases here</p>
            <Link to="/projects" className="btn btn-primary" style={{ marginTop: '1rem', width: 'auto' }}>
              Browse Projects
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
