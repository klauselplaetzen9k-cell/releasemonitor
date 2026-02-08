import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { projectsApi } from '../api/axios'

interface Project {
  id: number
  name: string
  source: string
  description: string | null
  avatar_url: string | null
  created_at: string
}

const SOURCE_LABELS: Record<string, string> = {
  github: 'GitHub',
  gitlab: 'GitLab',
  npm: 'npm',
  pypi: 'PyPI',
  docker: 'Docker Hub',
  crates: 'Crates.io',
  maven: 'Maven',
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    source: 'github',
    repo_url: '',
    description: '',
  })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const response = await projectsApi.list()
      setProjects(response.data)
    } catch (error) {
      console.error('Failed to fetch projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)

    try {
      await projectsApi.create(formData)
      setShowModal(false)
      setFormData({ name: '', source: 'github', repo_url: '', description: '' })
      fetchProjects()
    } catch (error) {
      console.error('Failed to create project:', error)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">Projects</h1>
          <p className="page-subtitle">Monitor releases from your favorite projects</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + Add Project
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading projects...</div>
      ) : projects.length > 0 ? (
        <div className="projects-grid">
          {projects.map((project) => (
            <Link key={project.id} to={`/projects/${project.id}`} className="project-card" style={{ textDecoration: 'none' }}>
              <div className="project-name">{project.name}</div>
              <span className="project-source">{SOURCE_LABELS[project.source] || project.source}</span>
              {project.description && (
                <p className="project-description">{project.description}</p>
              )}
            </Link>
          ))}
        </div>
      ) : (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon">📦</div>
            <h3>No projects yet</h3>
            <p>Add your first project to start monitoring releases</p>
            <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => setShowModal(true)}>
              Add Project
            </button>
          </div>
        </div>
      )}

      {showModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div className="card" style={{ width: '100%', maxWidth: '500px', margin: '1rem' }}>
            <h2 className="card-title" style={{ marginBottom: '1.5rem' }}>Add Project</h2>
            
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Project Name</label>
                <input
                  type="text"
                  className="form-input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  placeholder="e.g., React, Node.js"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Source</label>
                <select
                  className="form-input"
                  value={formData.source}
                  onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                >
                  <option value="github">GitHub</option>
                  <option value="gitlab">GitLab</option>
                  <option value="npm">npm</option>
                  <option value="pypi">PyPI</option>
                  <option value="docker">Docker Hub</option>
                  <option value="crates">Crates.io</option>
                  <option value="maven">Maven Central</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Repository URL</label>
                <input
                  type="url"
                  className="form-input"
                  value={formData.repo_url}
                  onChange={(e) => setFormData({ ...formData, repo_url: e.target.value })}
                  placeholder="e.g., https://github.com/facebook/react"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Description (optional)</label>
                <textarea
                  className="form-input"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  placeholder="Brief description of the project"
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                <button type="submit" className="btn btn-primary" disabled={submitting} style={{ flex: 1 }}>
                  {submitting ? 'Adding...' : 'Add Project'}
                </button>
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)} style={{ flex: 1 }}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
