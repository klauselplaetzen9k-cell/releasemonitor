import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { projectsApi, releasesApi, subscriptionsApi } from '../api/axios'
import { formatDistanceToNow } from 'date-fns'
import { marked } from 'marked'

interface Project {
  id: number
  name: string
  source: string
  description: string | null
  avatar_url: string | null
  created_at: string
  is_subscribed: boolean
}

interface Release {
  id: number
  version: string
  release_date: string | null
  changelog: string | null
  tag_name: string | null
  prerelease: boolean
  created_at: string
}

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [releases, setReleases] = useState<Release[]>([])
  const [loading, setLoading] = useState(true)
  const [subscribed, setSubscribed] = useState(false)

  useEffect(() => {
    if (id) {
      fetchProject()
      fetchReleases()
    }
  }, [id])

  const fetchProject = async () => {
    try {
      const response = await projectsApi.get(Number(id))
      setProject(response.data)
      setSubscribed(response.data.is_subscribed)
    } catch (error) {
      console.error('Failed to fetch project:', error)
    }
  }

  const fetchReleases = async () => {
    try {
      const response = await releasesApi.getProjectReleases(Number(id))
      setReleases(response.data)
    } catch (error) {
      console.error('Failed to fetch releases:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleSubscription = async () => {
    try {
      if (subscribed) {
        // Find and delete subscription
        const subs = await subscriptionsApi.list()
        const sub = subs.data.find((s: any) => s.project_id === Number(id))
        if (sub) {
          await subscriptionsApi.delete(sub.id)
        }
      } else {
        await subscriptionsApi.create({ project_id: Number(id) })
      }
      setSubscribed(!subscribed)
    } catch (error) {
      console.error('Failed to toggle subscription:', error)
    }
  }

  if (loading) {
    return <div className="loading">Loading project...</div>
  }

  if (!project) {
    return <div className="empty-state"><h3>Project not found</h3></div>
  }

  return (
    <div>
      <Link to="/projects" style={{ color: 'var(--text-secondary)', marginBottom: '1rem', display: 'inline-block' }}>
        ← Back to Projects
      </Link>

      <div className="card" style={{ marginTop: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1 className="page-title">{project.name}</h1>
            <span className="project-source">{project.source}</span>
            {project.description && (
              <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>{project.description}</p>
            )}
          </div>
          <button
            className={`btn ${subscribed ? 'btn-secondary' : 'btn-primary'}`}
            onClick={toggleSubscription}
            style={{ width: 'auto' }}
          >
            {subscribed ? '✓ Subscribed' : 'Subscribe'}
          </button>
        </div>
      </div>

      <h2 style={{ marginTop: '2rem', marginBottom: '1rem' }}>Releases</h2>

      {releases.length > 0 ? (
        <div className="release-list">
          {releases.map((release) => (
            <div key={release.id} className="card" style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <h3 style={{ margin: 0 }}>{release.version}</h3>
                    {release.prerelease && <span className="badge badge-warning">Pre-release</span>}
                  </div>
                  {release.release_date && (
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                      Released {formatDistanceToNow(new Date(release.release_date), { addSuffix: true })}
                    </p>
                  )}
                </div>
                {release.tag_name && (
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                    Tag: {release.tag_name}
                  </span>
                )}
              </div>
              
              {release.changelog && (
                <div
                  style={{ marginTop: '1rem', padding: '1rem', background: 'var(--background)', borderRadius: 'var(--radius)' }}
                  dangerouslySetInnerHTML={{ __html: marked.parse(release.changelog.slice(0, 500)) as string }}
                />
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="card">
          <div className="empty-state">
            <p>No releases found</p>
          </div>
        </div>
      )}
    </div>
  )
}
